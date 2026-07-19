package com.example.manager

import android.content.Context
import android.util.Log
import com.example.db.AppDatabase
import com.example.model.Message
import com.example.model.Reflexion
import com.example.model.Sender
import kotlinx.coroutines.flow.firstOrNull
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import org.json.JSONObject

class ReflexionEngine(private val context: Context) {
    private val db = AppDatabase.getDatabase(context)
    private val TAG = "AETHER_Reflexion"

    companion object {
        const val MAX_CONCLUSIONES_PROMPT = 3
        const val MAX_CHARS_PROMPT = 600
        const val VENTANA_MENSAJES = 12
        const val MIN_MENSAJES_NUEVOS = 6
    }

    suspend fun reflexionar(): String? {
        // Llamar a EvolutionScanner (asíncronamente o aquí)
        try {
            val scanner = EvolutionScanner(context)
            scanner.runScan()
        } catch (e: Exception) {
            Log.e(TAG, "Error en EvolutionScanner", e)
        }

        val allMessages = db.messageDao().getAllMessages().firstOrNull() ?: emptyList()
        val recientes = allMessages.takeLast(VENTANA_MENSAJES)

        if (!hayMaterialNuevo(recientes)) {
            return null
        }

        val convo = recientes.joinToString("\n") { "[${it.sender}] ${it.text.take(400)}" }
        val comparables = obtenerComparables(convo, 3)
        val comparablesText = if (comparables.isNotEmpty()) comparables.joinToString("\n") { "- $it" } else "(ninguna)"

        val prompt = """Eres el módulo de reflexión de AETHER. Analiza este fragmento
de conversación reciente entre AETHER y su usuario, y compáralo con conclusiones
de reflexiones anteriores si se aportan.

CONVERSACIÓN RECIENTE:
$convo

CONCLUSIONES PREVIAS COMPARABLES (puede estar vacío):
$comparablesText

Responde SOLO con un objeto JSON, sin markdown ni texto extra:
{
  "resumen": "qué ocurrió, 1-2 frases",
  "impacto_usuario": "efecto probable de las respuestas en el usuario, 1 frase",
  "impacto_propio": "qué debería ajustar el sistema, 1 frase",
  "comparacion": "en qué coincide o difiere de los casos previos, o 'sin precedentes'",
  "conclusion": "regla accionable y concreta para futuras respuestas, 1-2 frases",
  "tags": ["3-5", "palabras", "clave", "en", "minusculas"]
}"""

        try {
            val apiKey = com.example.BuildConfig.GROQ_API_KEY
            if (apiKey.isBlank() || apiKey == "YOUR_GROQ_API_KEY") return null

            val req = GroqRequest(
                model = "llama-3.3-70b-versatile",
                messages = listOf(
                    GroqMessage(role = "system", content = "Eres el motor de reflexión metacognitiva interno de AETHER."),
                    GroqMessage(role = "user", content = prompt)
                ),
                temperature = 0.3
            )
            val response = GroqRetrofitClient.service.generateContent("Bearer $apiKey", req)
            val jsonText = response.choices.firstOrNull()?.message?.content?.replace(Regex("```(json)?"), "")?.trim() ?: return null
            val startIdx = jsonText.indexOf('{')
            val endIdx = jsonText.lastIndexOf('}')
            
            if (startIdx != -1 && endIdx != -1) {
                val cleanJson = jsonText.substring(startIdx, endIdx + 1)
                val json = JSONObject(cleanJson)
                
                val conclusion = json.getString("conclusion")
                val tags = if (json.has("tags")) {
                    val tagsArray = json.getJSONArray("tags")
                    (0 until tagsArray.length()).joinToString(",") { tagsArray.getString(it) }
                } else ""
                
                val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
                sdf.timeZone = TimeZone.getTimeZone("UTC")
                
                val reflexion = Reflexion(
                    ts = sdf.format(Date()),
                    ultimoMsgTimestamp = recientes.last().timestampMs,
                    resumen = json.optString("resumen", ""),
                    impactoUsuario = json.optString("impacto_usuario", ""),
                    impactoPropio = json.optString("impacto_propio", ""),
                    comparacion = json.optString("comparacion", ""),
                    conclusion = conclusion,
                    tags = tags
                )
                
                db.reflexionDao().insertReflexion(reflexion)
                Log.d(TAG, "Reflexion generada y guardada: $conclusion")

                val tagsList = if (json.has("tags")) {
                    val tagsArray = json.getJSONArray("tags")
                    (0 until tagsArray.length()).map { tagsArray.getString(it) }
                } else emptyList()
                com.example.core.AetherCoreService.aplicarReflexion(
                    foco = json.optString("resumen", "Procesando entorno"),
                    prioridades = tagsList,
                    conclusion = conclusion
                )

                return conclusion
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error generating reflexion", e)
        }
        return null
    }

    private suspend fun hayMaterialNuevo(mensajes: List<Message>): Boolean {
        if (mensajes.isEmpty()) return false
        val ultimoReflexionado = db.reflexionDao().getLastReflexionTimestamp() ?: 0L
        val nuevos = mensajes.count { it.timestampMs > ultimoReflexionado }
        return nuevos >= MIN_MENSAJES_NUEVOS
    }

    private suspend fun obtenerComparables(texto: String, k: Int): List<String> {
        val terminos = Regex("[a-záéíóúñ]{4,}").findAll(texto.lowercase())
            .map { it.value }.toSet().take(12)
        
        val reflexiones = db.reflexionDao().getActiveReflexiones()
        if (terminos.isEmpty() || reflexiones.isEmpty()) return emptyList()

        val scored = reflexiones.map { ref ->
            val refText = (ref.conclusion + " " + ref.tags + " " + ref.resumen).lowercase()
            val score = terminos.count { refText.contains(it) }
            Pair(ref, score)
        }.filter { it.second > 0 }.sortedByDescending { it.second }.take(k)
        
        return scored.map { it.first.conclusion }
    }
    
    suspend fun conclusionesParaPrompt(mensajeUsuario: String): String {
        var relevantes = obtenerComparables(mensajeUsuario, MAX_CONCLUSIONES_PROMPT)
        if (relevantes.isEmpty()) {
            relevantes = db.reflexionDao().getActiveReflexiones().take(MAX_CONCLUSIONES_PROMPT).map { it.conclusion }
        }
        
        val bloque = relevantes.joinToString("\n") { "- $it" }.take(MAX_CHARS_PROMPT)
        if (bloque.isEmpty()) return ""
        return "\n[APRENDIZAJES DE REFLEXIONES PREVIAS]\n$bloque\n"
    }
}
