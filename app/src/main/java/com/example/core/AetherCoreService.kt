package com.example.core

import android.app.ActivityManager
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import android.os.Build
import android.os.IBinder
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit
import androidx.work.ExistingPeriodicWorkPolicy
import android.util.Log
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import org.json.JSONArray
import org.json.JSONObject

data class AetherState(
    var focoActual: String = "sin foco definido",
    var prioridades: MutableList<String> = mutableListOf(),
    var ultimaReflexion: Long = 0L,
    var conclusionReflexion: String = "",

    var nivelActivacion: Float = 0f,
    var ultimaInteraccion: Long = 0L,
    var interaccionesHoy: Int = 0,

    var bateriaPct: Int = -1,
    var cargando: Boolean = false,
    var ramDisponibleMb: Long = -1,
    var ramBaja: Boolean = false,
    var redTipo: String = "desconocida",

    var erroresRecientes: MutableList<String> = mutableListOf(),

    var timestamp: Long = System.currentTimeMillis()
) {
    fun toJson(): JSONObject = JSONObject().apply {
        put("foco_actual", focoActual)
        put("prioridades", JSONArray(prioridades))
        put("ultima_reflexion", ultimaReflexion)
        put("conclusion_reflexion", conclusionReflexion)
        put("nivel_activacion", nivelActivacion.toDouble())
        put("ultima_interaccion", ultimaInteraccion)
        put("interacciones_hoy", interaccionesHoy)
        put("bateria_pct", bateriaPct)
        put("cargando", cargando)
        put("ram_disponible_mb", ramDisponibleMb)
        put("ram_baja", ramBaja)
        put("red_tipo", redTipo)
        put("errores_recientes", JSONArray(erroresRecientes))
        put("timestamp", timestamp)
    }

    fun resumenParaPrompt(): String {
        val partes = mutableListOf<String>()
        partes.add("Foco actual: $focoActual.")
        if (prioridades.isNotEmpty())
            partes.add("Prioridades: ${prioridades.joinToString("; ")}.")
        partes.add("Batería: $bateriaPct%${if (cargando) " (cargando)" else ""}.")
        if (ramBaja)
            partes.add("ADVERTENCIA: memoria baja (${ramDisponibleMb}MB libres) — evita inferencia local.")
        partes.add("Red: $redTipo.")
        if (erroresRecientes.isNotEmpty())
            partes.add("Fallos recientes: ${erroresRecientes.takeLast(3).joinToString("; ")}.")
        if (conclusionReflexion.isNotBlank())
            partes.add("Última reflexión: $conclusionReflexion")
        return partes.joinToString(" ")
    }

    companion object {
        fun fromJson(json: JSONObject): AetherState = AetherState(
            focoActual = json.optString("foco_actual", "sin foco definido"),
            prioridades = json.optJSONArray("prioridades").toMutableStringList(),
            ultimaReflexion = json.optLong("ultima_reflexion", 0L),
            conclusionReflexion = json.optString("conclusion_reflexion", ""),
            nivelActivacion = json.optDouble("nivel_activacion", 0.0).toFloat(),
            ultimaInteraccion = json.optLong("ultima_interaccion", 0L),
            interaccionesHoy = json.optInt("interacciones_hoy", 0),
            erroresRecientes = json.optJSONArray("errores_recientes").toMutableStringList()
        )

        private fun JSONArray?.toMutableStringList(): MutableList<String> {
            val out = mutableListOf<String>()
            if (this != null) for (i in 0 until length()) out.add(getString(i))
            return out
        }
    }
}

class StateRepository(context: Context) :
    SQLiteOpenHelper(context, "aether_state.db", null, 1) {

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            """CREATE TABLE snapshot (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                json TEXT NOT NULL,
                updated_at INTEGER NOT NULL
            )"""
        )
        db.execSQL(
            """CREATE TABLE historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                json TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )"""
        )
    }

    override fun onUpgrade(db: SQLiteDatabase, old: Int, new: Int) { }

    fun guardar(state: AetherState, archivarEnHistorial: Boolean = false) {
        val ahora = System.currentTimeMillis()
        val json = state.toJson().toString()
        writableDatabase.use { db ->
            db.execSQL(
                "INSERT OR REPLACE INTO snapshot (id, json, updated_at) VALUES (1, ?, ?)",
                arrayOf(json, ahora)
            )
            if (archivarEnHistorial) {
                db.insert("historial", null, ContentValues().apply {
                    put("json", json)
                    put("created_at", ahora)
                })
                db.execSQL(
                    "DELETE FROM historial WHERE id NOT IN " +
                    "(SELECT id FROM historial ORDER BY id DESC LIMIT 500)"
                )
            }
        }
    }

    fun cargar(): AetherState? = try {
        readableDatabase.rawQuery(
            "SELECT json FROM snapshot WHERE id = 1", null
        ).use { c ->
            if (c.moveToFirst()) AetherState.fromJson(JSONObject(c.getString(0)))
            else null
        }
    } catch (e: Exception) {
        Log.e("AetherState", "Error cargando snapshot", e); null
    }

    fun historialReciente(n: Int = 50): List<JSONObject> {
        val out = mutableListOf<JSONObject>()
        readableDatabase.rawQuery(
            "SELECT json FROM historial ORDER BY id DESC LIMIT ?",
            arrayOf(n.toString())
        ).use { c -> while (c.moveToNext()) out.add(JSONObject(c.getString(0))) }
        return out
    }
}

class AetherCoreService : Service() {

    companion object {
        const val CANAL_ID = "aether_core"
        const val NOTIF_ID = 1001
        const val LATIDO_MS = 5 * 60 * 1000L
        const val ARCHIVO_CADA_N_LATIDOS = 6
        const val DECAIMIENTO_ACTIVACION = 0.85f

        @Volatile
        var estado: AetherState = AetherState()
            private set

        @Volatile
        private var instancia: AetherCoreService? = null

        fun registrarInteraccion() {
            estado.ultimaInteraccion = System.currentTimeMillis()
            estado.interaccionesHoy += 1
            estado.nivelActivacion = 1.0f
            instancia?.persistir()
        }

        fun registrarError(modulo: String, detalle: String) {
            val entrada = "[$modulo] $detalle"
            estado.erroresRecientes.add(entrada)
            while (estado.erroresRecientes.size > 20)
                estado.erroresRecientes.removeAt(0)
            Log.w("AetherCore", "Error registrado: $entrada")
            instancia?.persistir()
        }

        fun aplicarReflexion(foco: String, prioridades: List<String>, conclusion: String) {
            estado.focoActual = foco
            estado.prioridades = prioridades.toMutableList()
            estado.conclusionReflexion = conclusion
            estado.ultimaReflexion = System.currentTimeMillis()
            instancia?.persistir(archivar = true)
            instancia?.actualizarNotificacion()
        }

        fun contextoParaPrompt(): String = estado.resumenParaPrompt()

        fun arrancar(context: Context) {
            val intent = Intent(context, AetherCoreService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
                context.startForegroundService(intent)
            else
                context.startService(intent)
        }
    }

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private var latidoJob: Job? = null
    private var latidosDesdeArchivo = 0
    private lateinit var repo: StateRepository

    override fun onCreate() {
        super.onCreate()
        instancia = this
        repo = StateRepository(this)

        repo.cargar()?.let { previo ->
            estado = previo
            if (!esMismoDia(previo.timestamp, System.currentTimeMillis()))
                estado.interaccionesHoy = 0
        }

        crearCanalNotificacion()
        startForeground(NOTIF_ID, construirNotificacion())
        iniciarLatido()
        // Programar actualizacion automatica semanal
        val updateRequest = PeriodicWorkRequestBuilder<UpdateWorker>(7, TimeUnit.DAYS)
            .build()
        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "WeeklyUpdate",
            ExistingPeriodicWorkPolicy.KEEP,
            updateRequest
        )

        Log.i("AetherCore", "Servicio arrancado. Estado restaurado: ${estado.focoActual}")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        persistir(archivar = true)
        latidoJob?.cancel()
        scope.cancel()
        instancia = null
        super.onDestroy()
    }

    private fun iniciarLatido() {
        latidoJob = scope.launch {
            while (true) {
                try {
                    latido()
                } catch (e: Exception) {
                    Log.e("AetherCore", "Fallo en latido", e)
                    registrarError("core", "latido: ${e.message}")
                }
                delay(LATIDO_MS)
            }
        }
    }

    private fun latido() {
        leerBateria()
        leerMemoria()
        leerRed()

        val msSinActividad = System.currentTimeMillis() - estado.ultimaInteraccion
        if (msSinActividad > LATIDO_MS) {
            estado.nivelActivacion =
                (estado.nivelActivacion * DECAIMIENTO_ACTIVACION).coerceAtLeast(0f)
        }

        estado.timestamp = System.currentTimeMillis()

        latidosDesdeArchivo++
        val archivar = latidosDesdeArchivo >= ARCHIVO_CADA_N_LATIDOS
        if (archivar) latidosDesdeArchivo = 0
        persistir(archivar)

        actualizarNotificacion()
    }

    internal fun persistir(archivar: Boolean = false) {
        scope.launch(Dispatchers.IO) {
            try {
                repo.guardar(estado, archivar)
            } catch (e: Exception) {
                Log.e("AetherCore", "Fallo persistiendo estado", e)
            }
        }
    }

    private fun leerBateria() {
        val intent = registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
            ?: return
        val nivel = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
        val escala = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
        if (nivel >= 0 && escala > 0)
            estado.bateriaPct = (nivel * 100) / escala
        val status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
        estado.cargando = status == BatteryManager.BATTERY_STATUS_CHARGING ||
                status == BatteryManager.BATTERY_STATUS_FULL
    }

    private fun leerMemoria() {
        val am = getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val mi = ActivityManager.MemoryInfo()
        am.getMemoryInfo(mi)
        estado.ramDisponibleMb = mi.availMem / (1024 * 1024)
        estado.ramBaja = mi.lowMemory
    }

    private fun leerRed() {
        val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val caps = cm.getNetworkCapabilities(cm.activeNetwork)
        estado.redTipo = when {
            caps == null -> "sin_red"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "wifi"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "movil"
            else -> "otra"
        }
    }

    private fun crearCanalNotificacion() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val canal = NotificationChannel(
                CANAL_ID, "AETHER Core",
                NotificationManager.IMPORTANCE_LOW
            ).apply { description = "Estado interno persistente de AETHER" }
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(canal)
        }
    }

    private fun construirNotificacion(): Notification =
        NotificationCompat.Builder(this, CANAL_ID)
            .setContentTitle("AETHER activo")
            .setContentText(estado.focoActual)
            .setSmallIcon(android.R.drawable.ic_menu_compass)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .build()

    internal fun actualizarNotificacion() {
        getSystemService(NotificationManager::class.java)
            .notify(NOTIF_ID, construirNotificacion())
    }

    private fun esMismoDia(t1: Long, t2: Long): Boolean {
        val dia = 24 * 60 * 60 * 1000L
        return t1 / dia == t2 / dia
    }
}
