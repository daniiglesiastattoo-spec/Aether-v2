package com.example.manager

import android.content.Context
import android.util.Log
import com.example.db.AppDatabase
import com.example.model.EvolutionProposal
import org.json.JSONObject
import org.json.JSONArray
import java.security.MessageDigest
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import kotlinx.coroutines.flow.firstOrNull

class EvolutionScanner(private val context: Context) {
    private val db = AppDatabase.getDatabase(context)
    private val TAG = "AETHER_Evolution"
    private val maxProposals = 3
    private val categorias = listOf("parametros", "memoria", "arquitectura", "codigo", "rendimiento")

    private fun sha1(input: String): String {
        val bytes = MessageDigest.getInstance("SHA-1").digest(input.toByteArray())
        return bytes.joinToString("") { "%02x".format(it) }
    }

    private suspend fun gatherEvidence(): JSONObject {
        val ev = JSONObject()
        val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US)
        ev.put("fecha", sdf.format(Date()))

        // Reflexiones recientes
        try {
            val reflexiones = db.reflexionDao().getActiveReflexiones().take(15)
            val refArray = JSONArray()
            for (r in reflexiones) {
                val obj = JSONObject()
                obj.put("id", r.id)
                obj.put("conclusion", r.conclusion)
                obj.put("ts", r.ts)
                refArray.put(obj)
            }
            ev.put("reflexiones_recientes", refArray)
        } catch (e: Exception) {
            ev.put("reflexiones_recientes", "error_or_empty")
        }

        // Memoria total registros (messages in this case instead of memoria_episodica)
        try {
            val allMessages = db.messageDao().getAllMessages().firstOrNull() ?: emptyList()
            ev.put("memoria_total_registros", allMessages.size)
        } catch (e: Exception) {
            ev.put("memoria_total_registros", "error_or_empty")
        }

        // Propuestas previas
        try {
            val prev = db.evolutionProposalDao().getRecentProposals(20)
            val prevArray = JSONArray()
            for (p in prev) {
                val obj = JSONObject()
                obj.put("titulo", p.titulo)
                obj.put("categoria", p.categoria)
                obj.put("estado", p.estado)
                prevArray.put(obj)
            }
            ev.put("propuestas_previas", prevArray)
        } catch (e: Exception) {
            ev.put("propuestas_previas", "error_or_empty")
        }

        return ev
    }

    private fun buildPrompt(evidence: JSONObject): String {
        return """Eres el módulo de auto-análisis estructural de AETHER, un asistente
IA que corre en Android (4-6GB RAM), con routing híbrido local/Gemini, memoria SQLite y ciclos de reflexión.

Analiza la EVIDENCIA y detecta como máximo $maxProposals problemas
ESTRUCTURALES reales con propuesta de mejora. Reglas estrictas:
- Solo propuestas basadas en evidencia concreta. Si no hay evidencia
  suficiente de un problema, NO lo inventes.
- No repitas propuestas ya listadas en propuestas_previas.
- Nada cosmético. Solo: parametros, memoria, arquitectura, codigo, rendimiento.
- Sé brutalmente honesto. Si todo funciona bien, devuelve lista vacía.

Responde SOLO con JSON válido, sin markdown, con este formato:
{"propuestas": [{"categoria": "...", "titulo": "...", "problema": "...", "propuesta": "...", "evidencia": "...", "riesgo": "bajo|medio|alto"}]}

EVIDENCIA:
${evidence.toString().take(8000)}
"""
    }

    suspend fun runScan(): Int {
        try {
            val apiKey = com.example.BuildConfig.GEMINI_API_KEY
            if (apiKey.isBlank() || apiKey == "MY_GEMINI_API_KEY") return 0

            val evidence = gatherEvidence()
            val prompt = buildPrompt(evidence)

            val req = GenerateContentRequest(
                contents = listOf(Content(role = "user", parts = listOf(Part(text = prompt)))),
                generationConfig = GenerationConfig(temperature = 0.3)
            )
            val result = GeminiClient.generateContentSafe(apiKey, req, com.example.net.ApiPriority.BACKGROUND_REFLEXION)
            if (result.isFailure) return 0
            val jsonText = result.getOrNull()?.replace(Regex("```(json)?"), "")?.trim() ?: return 0
            
            val startIdx = jsonText.indexOf('{')
            val endIdx = jsonText.lastIndexOf('}')
            
            if (startIdx == -1 || endIdx == -1) return 0
            val cleanJson = jsonText.substring(startIdx, endIdx + 1)
            val data = JSONObject(cleanJson)
            
            var nuevas = 0
            if (data.has("propuestas")) {
                val propuestas = data.getJSONArray("propuestas")
                val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US)
                val ts = sdf.format(Date())
                for (i in 0 until minOf(propuestas.length(), maxProposals)) {
                    val p = propuestas.getJSONObject(i)
                    val cat = p.optString("categoria", "").lowercase()
                    if (cat !in categorias) continue
                    val titulo = p.optString("titulo", "").trim()
                    if (titulo.isEmpty()) continue
                    
                    val hash = sha1("$cat|${titulo.lowercase()}")
                    
                    val proposal = EvolutionProposal(
                        hash = hash,
                        timestamp = ts,
                        categoria = cat,
                        titulo = titulo,
                        problema = p.optString("problema", ""),
                        propuesta = p.optString("propuesta", ""),
                        evidencia = p.optString("evidencia", ""),
                        riesgo = p.optString("riesgo", "medio"),
                        estado = "pendiente"
                    )
                    try {
                        db.evolutionProposalDao().insertProposal(proposal)
                        nuevas++
                    } catch (e: Exception) {
                        // ignore duplicates
                    }
                }
            }
            Log.d(TAG, "Scan OK: $nuevas propuestas nuevas")
            return nuevas
        } catch (e: Exception) {
            com.example.core.AetherCoreService.registrarError("evolution", e.message ?: "Error desconocido")
            Log.e(TAG, "Scan ERROR", e)
            return 0
        }
    }

    suspend fun getPendingProposalsPrompt(): String {
        val pending = db.evolutionProposalDao().getPendingProposals(5)
        if (pending.isEmpty()) return ""
        
        val lineas = pending.joinToString("\n") { r ->
            "- [#${r.id} | ${r.categoria} | riesgo ${r.riesgo}] ${r.titulo}: ${r.problema} -> Propuesta: ${r.propuesta}"
        }
        
        return "PROPUESTAS DE AUTOMEJORA DETECTADAS EN SEGUNDO PLANO:\n" +
               lineas +
               "\nAl comenzar la conversación, informa a Dani de forma breve y honesta de estas propuestas. Ninguna se aplica sin su aprobación. Pregúntale si quiere aceptar, rechazar o ver detalles de alguna."
    }

    suspend fun markCommunicated() {
        db.evolutionProposalDao().markPendingAsCommunicated()
    }
}
