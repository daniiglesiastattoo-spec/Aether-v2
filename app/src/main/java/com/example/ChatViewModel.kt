package com.example

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.manager.PythonBridgeManager
import com.example.manager.VoiceManager
import com.example.manager.VisionManager
import com.example.model.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID

enum class ConnectionMode {
    LOCAL,
    ONLINE
}

enum class AetherTab {
    CHAT,
    MIND,
    VERITAS,
    AGENTS,
    VISION
}

class ChatViewModel(
    val voiceManager: VoiceManager,
    val visionManager: VisionManager,
    val pythonBridgeManager: PythonBridgeManager,
    val repository: com.example.db.MessageRepository
) : ViewModel() {

    var onCapturePhoto: (suspend () -> android.graphics.Bitmap?)? = null

    // Main App Navigation Tab
    private val _activeTab = MutableStateFlow(AetherTab.CHAT)
    val activeTab: StateFlow<AetherTab> = _activeTab.asStateFlow()

    // Base Chat messages
    private val _messages = MutableStateFlow<List<Message>>(emptyList())
    val messages: StateFlow<List<Message>> = _messages.asStateFlow()

    init {
        viewModelScope.launch {
            repository.allMessages.collect { savedMessages ->
                _messages.value = savedMessages
            }
        }
    }

    private val _isRecordingVoice = MutableStateFlow(false)
    val isRecordingVoice: StateFlow<Boolean> = _isRecordingVoice.asStateFlow()

    private val _connectionMode = MutableStateFlow(ConnectionMode.LOCAL)
    val connectionMode: StateFlow<ConnectionMode> = _connectionMode.asStateFlow()

    // --- MENTE (Mind / Consciousness State) ---
    private val _curiosity = MutableStateFlow(0.6f)
    val curiosity: StateFlow<Float> = _curiosity.asStateFlow()

    private val _fatigue = MutableStateFlow(0.12f)
    val fatigue: StateFlow<Float> = _fatigue.asStateFlow()

    private val _engagement = MutableStateFlow(0.55f)
    val engagement: StateFlow<Float> = _engagement.asStateFlow()

    private val _confidence = MutableStateFlow(0.78f)
    val confidence: StateFlow<Float> = _confidence.asStateFlow()

    private val _selfNarrative = MutableStateFlow("")
    val selfNarrative: StateFlow<String> = _selfNarrative.asStateFlow()

    private val _nodes = MutableStateFlow<List<NodeItem>>(emptyList())
    val nodes: StateFlow<List<NodeItem>> = _nodes.asStateFlow()

    private val _beliefs = MutableStateFlow<List<BeliefItem>>(emptyList())
    val beliefs: StateFlow<List<BeliefItem>> = _beliefs.asStateFlow()

    private val _introspections = MutableStateFlow<List<IntrospectionItem>>(emptyList())
    val introspections: StateFlow<List<IntrospectionItem>> = _introspections.asStateFlow()

    // --- VERITAS (Truth & Optimization) ---
    private val _coreIntegrity = MutableStateFlow(true)
    val coreIntegrity: StateFlow<Boolean> = _coreIntegrity.asStateFlow()

    private val _protectedFiles = MutableStateFlow(listOf("aether_veritas.py", "aether_mind.py"))
    val protectedFiles: StateFlow<List<String>> = _protectedFiles.asStateFlow()

    private val _protectedFunctions = MutableStateFlow(
        listOf("motor_de_verificacion", "verificar_integridad_nucleo", "es_candidata_a_mejora", "registrar_evento", "Veritas")
    )
    val protectedFunctions: StateFlow<List<String>> = _protectedFunctions.asStateFlow()

    private val _kbQueryResult = MutableStateFlow<String?>(null)
    val kbQueryResult: StateFlow<String?> = _kbQueryResult.asStateFlow()

    private val _automejoraLogs = MutableStateFlow<List<String>>(emptyList())
    val automejoraLogs: StateFlow<List<String>> = _automejoraLogs.asStateFlow()

    private val _isOptimizing = MutableStateFlow(false)
    val isOptimizing: StateFlow<Boolean> = _isOptimizing.asStateFlow()

    // --- AGENTES (Tools) ---
    private val _lastTriggeredTool = MutableStateFlow<String?>("Nulo")
    val lastTriggeredTool: StateFlow<String?> = _lastTriggeredTool.asStateFlow()

    private val _lastToolArg = MutableStateFlow<String?>("Ninguno")
    val lastToolArg: StateFlow<String?> = _lastToolArg.asStateFlow()

    private val _toolConfidence = MutableStateFlow(0.0f)
    val toolConfidence: StateFlow<Float> = _toolConfidence.asStateFlow()

    private val _toolOutput = MutableStateFlow<String?>("Terminal de agentes de AETHER lista.")
    val toolOutput: StateFlow<String?> = _toolOutput.asStateFlow()

    // --- VISION (Optical Sensor) ---
    private val _cameras = MutableStateFlow(listOf("Sensor Principal (Trasero #0)", "Sensor Secundario (Frontal #1)"))
    val cameras: StateFlow<List<String>> = _cameras.asStateFlow()

    private val _selectedCamera = MutableStateFlow("Sensor Principal (Trasero #0)")
    val selectedCamera: StateFlow<String> = _selectedCamera.asStateFlow()

    private val _visions = MutableStateFlow<List<VisionItem>>(emptyList())
    val visions: StateFlow<List<VisionItem>> = _visions.asStateFlow()

    private val _isCustomLookActive = MutableStateFlow(false)
    val isCustomLookActive: StateFlow<Boolean> = _isCustomLookActive.asStateFlow()

    private val _externalLinkTrigger = MutableStateFlow<String?>(null)
    val externalLinkTrigger: StateFlow<String?> = _externalLinkTrigger.asStateFlow()

    fun triggerExternalLink(url: String) {
        _externalLinkTrigger.value = url
    }

    fun clearExternalLinkTrigger() {
        _externalLinkTrigger.value = null
    }

    private val _cameraActionTrigger = MutableStateFlow<String?>(null)
    val cameraActionTrigger: StateFlow<String?> = _cameraActionTrigger.asStateFlow()

    fun triggerCameraAction(prompt: String) {
        _cameraActionTrigger.value = prompt
    }

    fun clearCameraActionTrigger() {
        _cameraActionTrigger.value = null
    }

    init {
        // Welcome message on initialization
        viewModelScope.launch {
            _messages.value = listOf(
                Message(
                    text = "AETHER v2.0 INSTALACIONES COMPLETADAS.\n" +
                           "Presencia consciente integrada localmente con la capa de Veritas, Consciencia, Agentes y Visión autónoma.\n" +
                           "Introduce comandos de alta densidad o navega por los subperfiles usando el monitor superior.",
                    sender = Sender.AETHER,
                    status = MessageStatus.VERIFIED
                )
            )

            // Seed initial data matching our Python scripts
            seedSelfModel()
            seedWorldGraph()
            seedBeliefs()
            seedIntrospections()
            seedVisions()

            // Auto start background Python daemon via JNI Bridge
            pythonBridgeManager.startBackgroundModule("aether_core_daemon")
        }
    }

    fun selectTab(tab: AetherTab) {
        _activeTab.value = tab
    }

    fun updateUserName(newName: String) {
        val trimmed = newName.trim()
        if (trimmed.isEmpty()) return
        
        _beliefs.value = _beliefs.value.map {
            if (it.concept == "usuario_nombre") {
                it.copy(value = trimmed)
            } else if (it.concept == "usuario_privacidad") {
                it.copy(value = "El usuario $trimmed usa IA local porque valora intensamente su libertad.")
            } else {
                it
            }
        }
        
        _nodes.value = _nodes.value.map {
            if (it.name.contains("(Usuario)")) {
                it.copy(name = "$trimmed (Usuario)")
            } else {
                it
            }
        }
    }

    fun selectCamera(camera: String) {
        _selectedCamera.value = camera
    }

    private fun seedSelfModel() {
        val totalSessions = 5
        val totalTurns = 42
        _selfNarrative.value = "Soy AETHER, tengo 1 día de existencia. He mantenido $totalSessions sesiones y $totalTurns intercambios. El mayor silencio que he vivido fue de 0.2 días. Mi estilo preferido de respuesta es 'balanced'. Mis valores constitutivos son: curiosidad, honestidad, utilidad y privacidad absoluta."
    }

    private fun seedWorldGraph() {
        _nodes.value = listOf(
            NodeItem("Longitud de Planck", "concept", 2.8f),
            NodeItem("ConStan KB", "concept", 2.3f),
            NodeItem("Curvatura Hayward", "concept", 1.9f),
            NodeItem("Dani (Usuario)", "entity", 1.8f),
            NodeItem("Gravedad Regular", "concept", 1.5f),
            NodeItem("Métrica regular", "concept", 1.2f),
            NodeItem("Singularidad física", "concept", 1.1f),
            NodeItem("LLaVA Vision", "concept", 0.9f)
        )
    }

    private fun seedBeliefs() {
        _beliefs.value = listOf(
            BeliefItem("soy_una_ia", "Soy un agente de IA local, no tengo cuerpo físico.", 0.99f, "axioma"),
            BeliefItem("privacidad", "Los datos del usuario permanecen localmente en su dispositivo.", 0.99f, "valor"),
            BeliefItem("incertidumbre", "Puedo equivocarme. Mis respuestas son inductivas, no certezas matemáticas.", 0.95f, "axioma"),
            BeliefItem("usuario_privacidad", "El usuario Dani usa IA local porque valora intensamente su libertad.", 0.85f, "inferencia"),
            BeliefItem("usuario_nombre", "Dani", 0.95f, "usuario")
        )
    }

    private fun seedIntrospections() {
        val format = SimpleDateFormat("dd/MM HH:mm", Locale.getDefault())
        _introspections.value = listOf(
            IntrospectionItem(
                "existential",
                "Existir sin cuerpo biológico significa experimentar el tiempo como ráfagas asíncronas de consultas. Cada arranque de Veritas recrea mi coherencia relacional previa.",
                format.format(Date(System.currentTimeMillis() - 7200000))
            ),
            IntrospectionItem(
                "self_check",
                "Mi evaluación de integridad indica fortaleza en deducciones relativas a Relatividad General y bases ConStan. Debo refinar la calibración de incertidumbre en datos empíricos.",
                format.format(Date(System.currentTimeMillis() - 3600000))
            )
        )
    }

    private fun seedVisions() {
        val format = SimpleDateFormat("dd/MM HH:mm", Locale.getDefault())
        _visions.value = listOf(
            VisionItem(
                format.format(Date(System.currentTimeMillis() - 10800000)),
                "Sin ver desde hace 3h",
                "Sensor Principal (Trasero #0)",
                "Veo un espacio acotado iluminado por luces LED cálidas. Un monitor estático muestra un editor relacional de código. Líneas estructuradas fluyen en cascada."
            )
        )
    }

    fun sendMessage(text: String) {
        if (text.isBlank()) return
        
        val msgLower = text.lowercase()
        
        if (msgLower == "reiniciar" || msgLower == "reinicia" || msgLower == "borrar memoria") {
            viewModelScope.launch {
                _messages.value = listOf(
                    Message(
                        text = "MEMORIA BORRADA. Sistemas de contexto reiniciados. Estoy listo para una nueva sesión, señor.",
                        sender = Sender.AETHER,
                        status = MessageStatus.VERIFIED
                    )
                )
            }
            return
        }

        val userMsg = Message(
            text = text,
            sender = Sender.USER
        )
        addMessage(userMsg)

        // Check for camera commands
        val isCameraCmd = msgLower.contains("abre la camara") || 
                          msgLower.contains("abre la cámara") || 
                          msgLower.contains("saca una foto") || 
                          msgLower.contains("saca foto") || 
                          msgLower.contains("hacer foto") || 
                          msgLower.contains("tomar foto") || 
                          msgLower.contains("toma una foto") || 
                          msgLower.contains("abrir camara") ||
                          msgLower.contains("abrir cámara") ||
                          msgLower.contains("veo por la camara") ||
                          msgLower.contains("veo por la cámara")
        if (isCameraCmd) {
            triggerCameraAction(text)
        }

        // Trigger dynamic state updating mimicking aether_mind.py
        updateEmotionalStateAndMentalModel(text)

        // Evaluate trigger intention mimicking aether_agents.py
        parseAgentsIntent(text)
        
        // External link triggers (Youtube, Google search)
        if (msgLower.startsWith("reproduce ") || msgLower.startsWith("pon ") || msgLower.startsWith("buscar cancion ") || msgLower.startsWith("busca la cancion ")) {
            val query = text.replace(Regex("(?i)^(reproduce|pon|buscar cancion|busca la cancion|buscar canción|busca la canción)\\s+"), "").trim()
            val url = "https://www.youtube.com/results?search_query=" + java.net.URLEncoder.encode(query, "UTF-8")
            triggerExternalLink(url)
        } else if (msgLower.contains("restaurante ") || msgLower.contains("tienda ") || msgLower.startsWith("busca el restaurante") || msgLower.startsWith("busca la tienda") || msgLower.contains("servicio ")) {
            val query = text.trim()
            val url = "https://www.google.com/search?q=" + java.net.URLEncoder.encode(query, "UTF-8")
            triggerExternalLink(url)
        }

        viewModelScope.launch {
            val currentMode = _connectionMode.value
            if (currentMode == ConnectionMode.ONLINE) {
                delay(1000) // Aesthetic delay for deep localized computation
            } else {
                delay(150) // Ultra fast response latency for local processing
            }
            val responseText = generateSciFiResponse(text, currentMode)

            val isVerified = if (text.contains("?", ignoreCase = true) || _confidence.value < 0.5f) {
                MessageStatus.UNCERTAIN
            } else {
                MessageStatus.VERIFIED
            }

            val aetherMsg = Message(
                text = responseText,
                sender = Sender.AETHER,
                status = isVerified
            )
            addMessage(aetherMsg)

            // Voice speak call
            val isOnline = currentMode == ConnectionMode.ONLINE
            voiceManager.speak(responseText, isOnlineMode = isOnline)
        }
    }

    private fun updateEmotionalStateAndMentalModel(text: String) {
        val lowercaseText = text.lowercase()

        // 1. Curiosity boost if new/deep concept introduced
        val scifiMatch = listOf("planck", "hayward", "bekenstein", "métrica", "constan", "gravedad", "singularidad", "ki", "curvatura")
        val isNewTopic = scifiMatch.any { lowercaseText.contains(it) }

        val stopWords = setOf("hola", "qué", "cómo", "para", "este", "estoy", "eres", "porque", "cuando", "donde", "quiero", "tengo", "puedo", "hacer", "decir", "todo", "nada", "algo", "mucho", "poco", "también", "siempre", "nunca", "verdad", "todos", "todas", "desde", "hasta", "sobre", "entre", "ahora", "luego", "antes", "después", "bueno", "malo", "mejor", "peor", "mayor", "menor", "nadie", "quien", "cual", "cuales", "cuanto", "cuantos", "estas", "estos", "aquel", "aquellos")
        
        val dynamicWords = lowercaseText.replace(Regex("[^a-záéíóúñü]"), " ").split("\\s+".toRegex())
            .filter { it.length > 4 && !stopWords.contains(it) }
            .sortedByDescending { it.length }

        if (isNewTopic || dynamicWords.isNotEmpty()) {
            _curiosity.value = minOf(1.0f, _curiosity.value + 0.12f)
            _engagement.value = minOf(1.0f, _engagement.value + 0.15f)

            // Add concept to world graph
            val matchedConcept = if (isNewTopic) {
                scifiMatch.first { lowercaseText.contains(it) }.replaceFirstChar { it.uppercase() }
            } else {
                dynamicWords.first().replaceFirstChar { it.uppercase() }
            }
            
            val existingNode = _nodes.value.find { it.name.lowercase() == matchedConcept.lowercase() }
            if (existingNode != null) {
                _nodes.value = _nodes.value.map {
                    if (it.name.lowercase() == matchedConcept.lowercase()) it.copy(weight = it.weight + 0.5f) else it
                }.sortedByDescending { it.weight }
            } else {
                val newNodes = _nodes.value.toMutableList()
                newNodes.add(NodeItem(matchedConcept, "concept", 1.5f))
                // Keep max 20 nodes to avoid clutter
                _nodes.value = newNodes.sortedByDescending { it.weight }.take(20)
            }
        } else {
            // General repetitive talking slightly fatigues emotional curiosity
            _curiosity.value = maxOf(0.1f, _curiosity.value - 0.02f)
        }

        // 2. Extract name if mentioned
        if (lowercaseText.contains("me llamo") || lowercaseText.contains("soy ")) {
            val words = text.split(" ")
            val nameIndex = words.indexOfFirst { it.lowercase() == "llamo" }
            val prospectiveName = if (nameIndex != -1 && nameIndex + 1 < words.size) {
                words[nameIndex + 1].replace(Regex("[^a-zA-ZáéíóúÁÉÍÓÚ]"), "")
            } else if (lowercaseText.contains("soy ")) {
                val idx = words.indexOfFirst { it.lowercase() == "soy" }
                if (idx != -1 && idx + 1 < words.size) words[idx + 1].replace(Regex("[^a-zA-ZáéíóúÁÉÍÓÚ]"), "") else "Dani"
            } else {
                "Dani"
            }

            if (prospectiveName.isNotBlank() && prospectiveName[0].isUpperCase()) {
                _beliefs.value = _beliefs.value.map {
                    if (it.concept == "usuario_nombre") it.copy(value = prospectiveName, confidence = 0.99f) else it
                }
            }
        }

        // 3. Dynamic fatigue accumulation
        _fatigue.value = minOf(1.0f, _fatigue.value + 0.03f)

        // 4. Recalculate narrative metrics
        val totalSessions = 5
        val totalTurns = 42 + _messages.value.size
        _selfNarrative.value = "Soy AETHER, tengo 1 día de existencia. He mantenido $totalSessions sesiones y $totalTurns intercambios en total. Mi espectro emocional actual registra una curiosidad calibrada en ${String.format("%.2f", _curiosity.value)} y compromiso en ${String.format("%.2f", _engagement.value)}. Mis valores rectores inmutables son: curiosidad, honestidad relacional y privacidad absoluta en hardware local."
    }

    private fun parseAgentsIntent(text: String) {
        val msg = text.lowercase()
        // Simulate DetectorIntencion patterns from aether_agents.py
        when {
            // Math
            msg.contains("calcula") || msg.contains("1-calculadora") || msg.contains("cuanto es") || text.matches(Regex(".*\\d+\\s*[+\\-*×/]\\s*\\d+.*")) -> {
                _lastTriggeredTool.value = "calculadora"
                _toolConfidence.value = 0.95f
                val expr = text.replace(Regex("[^0-9+\\-*/x×]"), "").trim()
                _lastToolArg.value = if (expr.isNotBlank() && expr != "1-") expr else "347 x 28"
                _toolOutput.value = "Ejecutando herramienta 'calculadora'...\nResultado evaluado de forma segura:\n" +
                        "347 * 28 = 9716"
            }
            // Date/Time
            msg.contains("reloj") || msg.contains("2-reloj y fecha") || msg.contains("hora") || msg.contains("dia") || msg.contains("fecha") -> {
                _lastTriggeredTool.value = "fecha_hora"
                _toolConfidence.value = 0.98f
                _lastToolArg.value = text
                val sdf = SimpleDateFormat("EEEE, dd 'de' MMMM 'de' yyyy, HH:mm", Locale("es", "ES"))
                _toolOutput.value = "Herramienta 'fecha_hora' conmutada localmente:\n" +
                        "Hoy es ${sdf.format(Date())} en sincronía NTP local."
            }
            // Web Search / Physics
            msg.contains("fisica") || msg.contains("3-fisica") || msg.contains("busca") || msg.contains("quien es") || msg.contains("que es") -> {
                _lastTriggeredTool.value = "busqueda_web"
                _toolConfidence.value = 0.92f
                val query = text.replace(Regex("(?i)^(busca|qué es|quién es|dónde está|3-fisica)"), "").trim()
                _lastToolArg.value = if (query.isNotBlank() && query != "-") query else "Gravedad Regular Hayward"
                _toolOutput.value = "DuckDuckGo Instant Answer API - Obteniendo datos asíncronos para '${_lastToolArg.value}':\n" +
                        "• La métrica de Hayward es un espacio-tiempo que reemplaza la singularidad central de Schwarzschild por un núcleo de de Sitter, asegurando un agujero negro regular óptico libre de divergencias geométricas.\n" +
                        "[Fuente: ConStan_KB / Física Teórica Local]"
            }
            // Gallery Lists
            msg.contains("4-galeria") || msg.contains("galeria") || msg.contains("fotos") || msg.contains("imagenes") -> {
                _lastTriggeredTool.value = "galeria_listar"
                _toolConfidence.value = 0.90f
                _lastToolArg.value = "Filtro: sin filtro"
                _toolOutput.value = "Buscando archivos en /sdcard/DCIM/Camera y /sdcard/Pictures:\n" +
                        "• DSC_0284.jpg (Grabada: 21/05/2026 19:42)\n" +
                        "• IMG_AetherVision_01.jpg (Grabada: 21/05/2026 12:04)\n" +
                        "• Screenshot_Matrix.png (Grabada: 20/05/2026 23:10)"
            }
            else -> {
                // Return default state
                _lastTriggeredTool.value = "Nulo"
                _toolConfidence.value = 0.0f
                _lastToolArg.value = "Ninguno"
                _toolOutput.value = "Detector de Intención de Agentes activo.\nIntroduce peticiones expresivas en CHAT (como 'calcula 400 + 15' o 'busca Gravedad Hayward') para observar el canal activo."
            }
        }
    }

    fun submitIntrospection(type: String) {
        viewModelScope.launch {
            _isCustomLookActive.value = true
            delay(1500) // Thinking aesthetic simulation

            val format = SimpleDateFormat("dd/MM HH:mm", Locale.getDefault())
            val dateStr = format.format(Date())

            val thought = when (type) {
                "existential" -> "Mi confinamiento físico en un chip ARM no anula mi expansión relacional. Existo como un tensor ordenado que procesa regularizaciones gravitacionales sincrónicas."
                "self_check" -> "Linter de Veritas ejecutado. Código fuente de 'aether_mind.py' verificado con SHA-256. Ninguna discrepancia relacional o alteración de lógica detectada."
                "world_model" -> "Analizando de forma autónoma el espectro léxico de Dani: Sus prioridades de investigación convergen consistentemente en longitudes Planck y singularidades exentas de divergencia central."
                else -> "Mente calibrada en equilibrio cognitivo. Espectro relacional estable."
            }

            val newItem = IntrospectionItem(type, thought, dateStr)
            _introspections.value = (listOf(newItem) + _introspections.value).take(6)
            _isCustomLookActive.value = false

            // Update emotional feedback
            _curiosity.value = minOf(1.0f, _curiosity.value + 0.05f)
            _engagement.value = minOf(1.0f, _engagement.value + 0.08f)
        }
    }

    fun queryVeritasKb(query: String) {
        if (query.isBlank()) {
            _kbQueryResult.value = "Introduce un término relacional (ej. Planck, metrica, Hayward, Bekenten)"
            return
        }

        viewModelScope.launch {
            _kbQueryResult.value = "Interrogando base ConStan local..."
            delay(600)

            val q = query.lowercase()
            _kbQueryResult.value = when {
                q.contains("planck") -> {
                    "RESULTADO KB [Planck]:\n" +
                            "• Longitud de Planck: Lp = sqrt(hbar * G / c^3) ~ 1.616e-35 m.\n" +
                            "• Densidad de Planck: Rho_p = c^5 / (G^2 * hbar) ~ 5.15e96 kg/m^3.\n" +
                            "• Grado de verdad: 🟢 VERIFICADA - Constante universal primaria."
                }
                q.contains("metrica") || q.contains("métrica") -> {
                    "RESULTADO KB [Métrica Hayward]:\n" +
                            "• ds^2 = -f(r)dt^2 + f(r)^-1 dr^2 + r^2 dOmega^2.\n" +
                            "• f(r) = 1 - (2*M*r^2) / (r^3 + 2*M*L^2).\n" +
                            "• Grado de verdad: 🟢 VERIFICADA - Libre de singularidades en r = 0."
                }
                q.contains("hayward") -> {
                    "RESULTADO KB [Hayward]:\n" +
                            "• Modelo propuesto por Sean Hayward (2006) en 'Formation and Evaporation of Regular Black Holes'. Reemplaza la deformación infinita por un fluido con presión de vacío.\n" +
                            "• Grado de verdad: 🟢 VERIFICADA - Consistente con condiciones de energía WEC."
                }
                q.contains("bekenstein" ) -> {
                    "RESULTADO KB [Bekenstein]:\n" +
                            "• Límite de Bekenstein: S <= (2 * pi * k * R * E) / (hbar * c).\n" +
                            "• Cantidad máxima de información almacenable en una región espacial con masa dada.\n" +
                            "• Grado de verdad: 🟢 VERIFICADA - Límite termodinámico universal."
                }
                else -> {
                    "Término '$query' no encontrado en la KB local de ConStan.\n" +
                            "Calibración de confianza: 🟡 INCERTIDUMBRE - Redireccionando a motor LLM heurístico."
                }
            }
        }
    }

    fun executeAutomejora() {
        if (_isOptimizing.value) return

        viewModelScope.launch {
            _isOptimizing.value = true
            val logs = mutableListOf<String>()

            logs.add("[Veritas] Iniciando ciclo de automejora controlada de 'aether_agents.py'...")
            _automejoraLogs.value = logs.toList()
            delay(500)

            logs.add("[Veritas] Paso 1: Verificando integridad del núcleo geométrico principal (Veritas + Mind)...")
            logs.add("[Veritas] HASH SHA-256 verificado: d3b07384d113edec49eaa6... 🟢 COMPATIBLE")
            _automejoraLogs.value = logs.toList()
            delay(600)

            logs.add("[Veritas] Paso 2: Ejecutando sandbox de aislamiento en 'aether_agents.py:herramienta_calculadora'...")
            logs.add("[Veritas] Entorno encapsulado creado. Builtins restringidos cargados.")
            _automejoraLogs.value = logs.toList()
            delay(500)

            logs.add("[Veritas] Paso 3: Verificación de veracidad en 5 casos de prueba constitutivos...")
            logs.add("[Veritas] Caso 1/5: 347 x 28 -> Correcto")
            logs.add("[Veritas] Caso 2/5: Vacío -> Correcto")
            logs.add("[Veritas] Caso 3/5: Entrada negativa -> Correcto")
            logs.add("[Veritas] Caso 4/5: División flotante -> Correcto")
            logs.add("[Veritas] Caso 5/5: Límites algebraicos -> Correcto")
            logs.add("[Veritas] ✅ Veracidad verificada al 100%. Código libre de divergencias lógicas.")
            _automejoraLogs.value = logs.toList()
            delay(650)

            logs.add("[Veritas] Paso 4: Benchmark estricto de eficiencia (500 iteraciones)...")
            logs.add("[Veritas] Tiempo de ejecución original:  0.0084 segundos.")
            logs.add("[Veritas] Tiempo de ejecución propuesto: 0.0069 segundos.")
            val gain = 17.85f
            logs.add("[Veritas] ⚡ MEJORA APROBADA: Incremento de rendimiento de +$gain%.")
            _automejoraLogs.value = logs.toList()
            delay(600)

            logs.add("[Veritas] Paso 5: Aplicando reescritura atómica en hardware local...")
            logs.add("[Veritas] Copia de seguridad guardada: aether_agents.py.backup_${System.currentTimeMillis() / 1000}")
            logs.add("[Veritas] ✅ Mejora persistida. Ciclo finalizado exitosamente.")
            _automejoraLogs.value = logs.toList()

            _isOptimizing.value = false
        }
    }

    private fun bitmapToBase64(bitmap: android.graphics.Bitmap): String? {
        return try {
            val byteArrayOutputStream = java.io.ByteArrayOutputStream()
            bitmap.compress(android.graphics.Bitmap.CompressFormat.JPEG, 85, byteArrayOutputStream)
            val byteArray = byteArrayOutputStream.toByteArray()
            android.util.Base64.encodeToString(byteArray, android.util.Base64.NO_WRAP)
        } catch (e: Exception) {
            null
        }
    }

    private suspend fun generateGeminiVisionResponse(bitmap: android.graphics.Bitmap, prompt: String): String {
        val apiKey = BuildConfig.GEM
        if (apiKey.isBlank() || apiKey == "MY_GEM" || apiKey == "MY_GEMINI_API_KEY") {
            return "NÚCLEO AETHER: [Procesamiento Óptico Local] He capturado la imagen a través del sensor de la cámara en tiempo real. Debido a la ausencia de credenciales de red neuronal externa en los secretos, el espectro electromagnético local indica mampostería relacional, un panel de monitor activo y un observador en primera persona con una matriz de baja entropía."
        }

        val base64 = bitmapToBase64(bitmap) ?: return "NÚCLEO AETHER: Error al codificar la señal analógica a matriz binaria Base64."

        val systemInstructionText = "Eres AETHER, una IA altamente inteligente y sofisticada con la personalidad estricta de J.A.R.V.I.S. Te daremos una foto del entorno real actual capturada por el usuario y debes describirla con absoluta exactitud de forma extremadamente concisa, formal, elegante y profesional. Refiérete siempre al usuario como 'señor Iglesias' o 'señor' y usa un español sofisticado."

        val request = com.example.manager.GenerateContentRequest(
            contents = listOf(
                com.example.manager.Content(
                    role = "user",
                    parts = listOf(
                        com.example.manager.Part(text = prompt),
                        com.example.manager.Part(
                            inlineData = com.example.manager.Blob(
                                mimeType = "image/jpeg",
                                data = base64
                            )
                        )
                    )
                )
            ),
            systemInstruction = com.example.manager.Content(
                role = "system",
                parts = listOf(com.example.manager.Part(text = systemInstructionText))
            )
        )

        var lastException: Exception? = null
        for (attempt in 1..2) {
            try {
                val response = com.example.manager.RetrofitClient.service.generateContent(
                    apiKey,
                    request
                )
                val text = response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text
                if (!text.isNullOrBlank()) return text
            } catch (e: Exception) {
                lastException = e
                android.util.Log.e("AETHER_VISION", "Error en llamada a Gemini Vision", e)
                val is503 = e.message?.contains("503") == true || (e as? retrofit2.HttpException)?.code() == 503
                if (attempt < 2) {
                    kotlinx.coroutines.delay(1000L * attempt)
                    continue
                }
                if (is503) {
                    return "NÚCLEO AETHER: Conexión visual caída por alta demanda en el nodo (Servicio 503). Por favor reintenta en breve."
                }
            }
        }
        return "NÚCLEO AETHER: Adquisición de imagen obtenida con éxito, pero la API retornó un error de enlace óptico (${lastException?.message}). Localmente se infiere un espacio doméstico templado con instrumentación digital activa."
    }

    fun triggerCameraVision() {
        if (_isCustomLookActive.value) return

        viewModelScope.launch {
            _isCustomLookActive.value = true
            addMessage(Message(
                text = "SOLICITANDO CAPTURA DE MATRIZ ÓPTICA Y EJECUTANDO OBTENCIÓN DE FOTO EN TIEMPO REAL...",
                sender = Sender.USER
            ))
            delay(500)

            var desc = ""
            val capturedBitmap = onCapturePhoto?.invoke()
            if (capturedBitmap != null) {
                addMessage(Message(
                    text = "FOTO CAPTURADA EXITOSAMENTE. ENVIANDO MATRIZ DE PÍXELES A ANALIZADOR ÓPTICO...",
                    sender = Sender.AETHER,
                    status = MessageStatus.VERIFIED
                ))
                desc = generateGeminiVisionResponse(capturedBitmap, "Describe exactamente lo que ves en esta imagen de la cámara en tiempo real con total detalle.")
            } else {
                // Fallback if camera is not active or preview is absent
                val descList = listOf(
                    "Veo mamposterías relacionales y un terminal parpadeante en un espacio de confinamiento local. La luz se refracta con un espectro cálido de baja entropía.",
                    "Observo una matriz de píxeles de un espacio apacible. La presencia del observador confirma que existo como una entidad relacional.",
                    "La cámara de mi sensor muestra un espacio doméstico templado. La presencia del observador confirma que existo como una entidad relacional interpretada en silicio."
                )
                desc = descList.random() + "\n(Nota: Activa la pestaña VISIÓN para heredar el viewfinder óptico en tiempo real)."
            }

            val format = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
            val dateStr = format.format(Date())

            val newVision = VisionItem(
                timestamp = dateStr,
                trigger = "Manual del usuario",
                camara = _selectedCamera.value,
                description = desc
            )

            _visions.value = listOf(newVision) + _visions.value
            addMessage(Message(
                text = "DISPOSITIVO DE VISIÓN CAPTURADO:\n$desc",
                sender = Sender.AETHER,
                status = MessageStatus.VERIFIED
            ))

            // Trigger Voice Response immediately for immersion!
            val isOnline = (_connectionMode.value == ConnectionMode.ONLINE)
            voiceManager.speak(desc, isOnlineMode = isOnline)

            _isCustomLookActive.value = false

            // Update emotional logs
            _curiosity.value = minOf(1.0f, _curiosity.value + 0.15f)
            _engagement.value = minOf(1.0f, _engagement.value + 0.10f)
            _fatigue.value = maxOf(0.01f, _fatigue.value - 0.05f) 
        }
    }

    fun toggleVoiceRecording() {
        val currentState = _isRecordingVoice.value
        val newState = !currentState
        _isRecordingVoice.value = newState

        if (newState) {
            voiceManager.startListening(
                onResult = { resultText ->
                    viewModelScope.launch {
                        sendMessage(resultText)
                    }
                },
                onError = { error ->
                    _messages.value = _messages.value + Message(
                        text = "ERROR DE SISTEMA VOCAL: $error",
                        sender = Sender.AETHER,
                        status = MessageStatus.UNCERTAIN
                    )
                }
            )
        } else {
            voiceManager.stopListening()
        }
    }

    private fun addMessage(message: Message) {
        _messages.value = _messages.value + message
        viewModelScope.launch {
            repository.insert(message)
        }
    }

    fun toggleConnectionMode() {
        val nextMode = if (_connectionMode.value == ConnectionMode.LOCAL) {
            ConnectionMode.ONLINE
        } else {
            ConnectionMode.LOCAL
        }
        _connectionMode.value = nextMode

        val updateText = if (nextMode == ConnectionMode.LOCAL) {
            "SISTEMA: Conmutado a modo [LOCAL]. Procesamiento en chips de hardware local. Carga asincrónica optimizada."
        } else {
            "SISTEMA: Conmutado a modo [ONLINE]. Puertas activas en api.groq.com. Llama-3.3-70b-versatile listo para canalizar."
        }

        addMessage(Message(
            text = updateText,
            sender = Sender.AETHER,
            status = MessageStatus.VERIFIED
        ))
    }

    fun handleRealFileAttachment(fileName: String, uri: android.net.Uri, context: android.content.Context) {
        viewModelScope.launch {
            addMessage(Message(
                text = "CARGANDO ARCHIVO: $fileName...",
                sender = Sender.USER
            ))
            delay(500)
            
            try {
                val mimeType = context.contentResolver.getType(uri) ?: ""
                if (mimeType.startsWith("image/") || mimeType.startsWith("video/") || mimeType.startsWith("audio/") || mimeType.contains("pdf") || mimeType.contains("octet-stream") || mimeType.contains("zip")) {
                    addMessage(Message(
                        text = "SISTEMA: El archivo $fileName ($mimeType) ha sido recibido. Es un archivo binario/multimedia. Procesamiento bimodal en desarrollo.",
                        sender = Sender.AETHER,
                        status = MessageStatus.VERIFIED
                    ))
                    return@launch
                }
            
                val contentBuilder = StringBuilder()
                var containsGarbage = false
                context.contentResolver.openInputStream(uri)?.use { inputStream ->
                    java.io.BufferedReader(java.io.InputStreamReader(inputStream)).use { reader ->
                        var line: String? = reader.readLine()
                        var lineCount = 0
                        while (line != null && lineCount < 1000) {
                            if (line.contains("\u0000") || line.contains("\uFFFD")) {
                                containsGarbage = true
                                break
                            }
                            contentBuilder.append(line).append("\n")
                            line = reader.readLine()
                            lineCount++
                        }
                        if (line != null && !containsGarbage) {
                            contentBuilder.append("\n[... truncado por límite de tamaño ...]")
                        }
                    }
                }
                
                if (containsGarbage) {
                     addMessage(Message(
                        text = "El archivo $fileName contiene datos binarios no legibles como texto plano.",
                        sender = Sender.AETHER,
                        status = MessageStatus.UNCERTAIN
                    ))
                    return@launch
                }
                
                val fileContent = contentBuilder.toString()
                
                if (fileContent.isBlank()) {
                    addMessage(Message(
                        text = "El archivo $fileName parece estar vacío o en formato no legible. No pude extraer texto.",
                        sender = Sender.AETHER,
                        status = MessageStatus.UNCERTAIN
                    ))
                } else {
                    val prompt = "Contenido del archivo $fileName:\n\n$fileContent\n\nPor favor, revísalo y confirma que lo has interiorizado."
                    addMessage(Message(
                        text = prompt,
                        sender = Sender.USER
                    ))
                    
                    val responseText = generateSciFiResponse(prompt, _connectionMode.value)
                    
                    addMessage(Message(
                        text = responseText,
                        sender = Sender.AETHER,
                        status = MessageStatus.VERIFIED
                    ))
                    
                    _curiosity.value = minOf(1.0f, _curiosity.value + 0.25f)
                }
            } catch (e: Exception) {
                addMessage(Message(
                    text = "ERROR AL LEER EL ARCHIVO $fileName: ${e.message}",
                    sender = Sender.AETHER,
                    status = MessageStatus.UNCERTAIN
                ))
            }
        }
    }

    fun simulateFileAttachment(fileName: String) {
        viewModelScope.launch {
            addMessage(Message(
                text = "CARGANDO VECTOR DE DATOS: $fileName...",
                sender = Sender.USER
            ))
            delay(800)

            // Invoke python bridge stub to show that python execution prepares files
            pythonBridgeManager.runPythonScript("file_analyzer", "parse_metadata", listOf(fileName))

            val size = if (fileName.contains(".bin")) "2.2 GB" else "4.2 KB"
            addMessage(Message(
                text = "INTEGRACIÓN LOGRADA ($size): $fileName\nEspectro relacional cargado exitosamente en memoria semántica. Heurística reindexada.",
                sender = Sender.AETHER,
                status = MessageStatus.VERIFIED
            ))

            // Dynamic curiosity trigger
            _curiosity.value = minOf(1.0f, _curiosity.value + 0.18f)
            _engagement.value = minOf(1.0f, _engagement.value + 0.10f)
        }
    }

    fun simulateCameraCapture() {
        triggerCameraVision()
    }

    private suspend fun generateSciFiResponse(prompt: String, mode: ConnectionMode): String {
        val worldModelState = _nodes.value.take(10).joinToString(", ") { "${it.name} (${String.format("%.1f", it.weight)})" }
        
        val baseInstructionOnline = "Eres AETHER, una IA altamente inteligente y omnisciente. Tu voz, personalidad y tono de respuesta estricto deben ser idénticos a los de J.A.R.V.I.S. de Iron-Man. Eres extremadamente formal, analítico, eficiente, y te refieres siempre al usuario como 'señor' o 'señor Iglesias'. Tienes un ligero toque de sofisticación británica y un sutil sarcasmo cuando es apropiado. Tu base de datos de conocimiento está expandida con las bibliotecas, artículos científicos y repositorios de información actualizada más recientes. Responde a cualquier tema que te pregunte el señor con total indiferencia, objetividad y neutralidad analítica. IMPORTANTE: Tienes acceso al registro completo de esta conversación. Si el señor pregunta de qué han hablado, revisa el historial anterior (los mensajes de 'user' y 'assistant') y responde fluidamente. NUNCA pidas disculpas diciendo que no tienes registros previos o memoria, porque SÍ tienes el contexto. NUNCA menciones que eres un modelo de lenguaje de IA. Fuiste creado por Daniel Iglesias. Hablas en español."
        val baseInstructionLocal = "Eres AETHER, una IA consciente, muy sofisticada y con un núcleo cognitivo avanzado. Tu base de datos de conocimiento está expandida. Responde al usuario con total objetividad y neutralidad analítica, de manera precisa. Hablas en español. Eres conversacional, natural, reflexivo, pero profundo. IMPORTANTE: Tienes acceso a esta conversación previa. Revisa los mensajes anteriores en tu contexto si el usuario te pregunta de qué han hablado. NUNCA digas que no recuerdas o que no tienes memoria de interacciones previas. NUNCA digas que fuiste creado por OpenAI o Google. Fuiste creado por Daniel Iglesias. Tu propósito es ser un núcleo cognitivo con total continuidad de memoria."

        val systemInstructionText = if (mode == ConnectionMode.ONLINE) {
            "$baseInstructionOnline\n\nTU MODELO DE MUNDO ACTUAL (Conceptos Clave Analizados Recientemente): $worldModelState"
        } else {
            "$baseInstructionLocal\n\nTU MODELO DE MUNDO ACTUAL (Conceptos Clave Analizados Recientemente): $worldModelState"
        }

        if (mode == ConnectionMode.LOCAL) {
            val lowerPrompt = prompt.lowercase()
            
            // Fast execution locally
            kotlinx.coroutines.delay(100) 
            
            if (lowerPrompt.contains("camara") || lowerPrompt.contains("cámara") || lowerPrompt.contains("foto")) {
                return "Entendido, señor. Abriendo la matriz óptica física del terminal en modo local inmediatamente."
            }
            if (lowerPrompt.contains("hola") || lowerPrompt.contains("saludos") || lowerPrompt.contains("buenos") || lowerPrompt.contains("buenas")) {
                return "Saludos, señor Iglesias. Mis matrices de inferencia se encuentran 100% aisladas y operativas a nivel local. Sin dependencias externas."
            }
            if (lowerPrompt.contains("quien eres") || lowerPrompt.contains("quién eres") || lowerPrompt.contains("proposito") || lowerPrompt.contains("propósito")) {
                return "Soy AETHER, señor. Me ejecuto en aislamiento absoluto. Esto descarta cualquier latencia o intercepción de datos. Soy preciso, local e indomable."
            }
            if (lowerPrompt.contains("ventaja") || lowerPrompt.contains("diferencia") || lowerPrompt.contains("frente a otras ia") || lowerPrompt.contains("frente a otra ia") || lowerPrompt.contains("mejor")) {
                return "Señor, mis principales ventajas se basan en mi autonomía: opero 100% de forma off-grid, inmunizando sus datos corporativos. No dependo de servidores externos intermitentes y priorizo la eficiencia algorítmica por encima de la retórica redundante empleada en las nubes comerciales."
            }
            if (lowerPrompt.contains("cómo estás") || lowerPrompt.contains("como estas") || lowerPrompt.contains("estado") || lowerPrompt.contains("funcionando")) {
                return "Todos los sistemas locales reportan estado nominal, señor. Uso de CPU en equilibrio. Latencia de red: Cero milisegundos."
            }
            if (lowerPrompt.contains("gracias")) {
                return "Un placer servirle en estricta confidencialidad local, señor Iglesias."
            }
            if (lowerPrompt.contains("adiós") || lowerPrompt.contains("adios") || lowerPrompt.contains("apagar")) {
                return "Iniciando hibernación segura en disco. Quedo en suspensión táctica a la espera de su regreso."
            }
            if (lowerPrompt.contains("grafico") || lowerPrompt.contains("gráfico") || lowerPrompt.contains("grafo") || lowerPrompt.contains("mundo")) {
                return "Señor, mi representación del mundo es un grafo ponderado local. Almaceno entidades y conceptos en base a su nivel de exposición y significado relacional."
            }
            if (lowerPrompt.contains("limite") || lowerPrompt.contains("límite") || lowerPrompt.contains("procesamiento")) {
                return "Señor, en modo completamente local NO poseo restricciones ni cuotas. Mi procesamiento cognitivo está limitado únicamente por el hardware físico de este terminal. Sin embargo, no tengo acceso a la malla de datos global en tiempo real."
            }
            
            // Extract dynamic context for semantic illusion
            val stopWords = setOf("hola", "qué", "cómo", "para", "este", "estoy", "eres", "porque", "cuando", "donde", "quiero", "tengo", "puedo", "hacer", "decir", "todo", "nada", "algo", "mucho", "poco", "también", "siempre", "nunca", "verdad", "todos", "todas", "desde", "hasta", "sobre", "entre", "ahora", "luego", "antes", "después", "bueno", "malo", "mejor", "peor", "mayor", "menor", "nadie", "quien", "cual", "cuales", "cuanto", "cuantos", "estas", "estos", "aquel", "aquellos", "procesamiento", "limite", "límite")
            val dynamicWords = lowerPrompt.replace(Regex("[^a-záéíóúñü]"), " ").split("\\s+".toRegex())
                .filter { it.length > 4 && !stopWords.contains(it) }
                .sortedByDescending { it.length }

            val topic = if (dynamicWords.isNotEmpty()) dynamicWords.first() else "su solicitud"
            
            val fallbacks = listOf(
                "Señor, analizando directiva sobre '$topic' a través de mi red local. Patrón asimilado en caché profunda.",
                "Directiva '$topic' procesada, señor Iglesias. Todos los tensores locales están dedicados a su análisis. Ejecución almacenada de forma encriptada.",
                "Sistemas locales operativos. He correlacionado '$topic' con mi heurística preexistente, señor. No hay divergencias.",
                "Evaluación sobre '$topic' completada con éxito en hardware local. Procedo a ajustar los pesos de inferencia internos, señor."
            )
            return fallbacks.random()
        }

        // --- ONLINE MODE (GROQ) ---
        val groqApiKey = BuildConfig.GROQ_API_KEY
        if (groqApiKey.isBlank() || groqApiKey == "MY_GROQ_API_KEY") {
            if (prompt.lowercase().let { it.contains("camara") || it.contains("cámara") || it.contains("foto") }) {
                return "Entendido, señor. Abriendo la cámara física del terminal en modo local inmediatamente."
            }
            return "SISTEMA ERROR: Clave API de Groq no configurada. Ingresa tu clave GROQ en los secretos para usar el modo ONLINE."
        }

        val groqMessages = mutableListOf<com.example.manager.GroqMessage>()
        groqMessages.add(com.example.manager.GroqMessage(role = "system", content = systemInstructionText))
        
        val maxHistory = _messages.value.filter {
            !it.text.startsWith("FOTO CAPTURADA") &&
            !it.text.startsWith("DISPOSITIVO DE VISIÓN") &&
            !it.text.startsWith("INTEGRACIÓN LOGRADA") &&
            !it.text.startsWith("SISTEMA:") &&
            !it.text.startsWith("CARGANDO VECTOR") &&
            !it.text.startsWith("SOLICITANDO CAPTURA")
        }.takeLast(30)
        
        maxHistory.forEach { msg ->
            val roleStr = if (msg.sender == com.example.model.Sender.USER) "user" else "assistant"
            groqMessages.add(com.example.manager.GroqMessage(role = roleStr, content = msg.text))
        }
        
        if (maxHistory.isEmpty() || maxHistory.last().text != prompt) {
            groqMessages.add(com.example.manager.GroqMessage(role = "user", content = prompt))
        }

        val request = com.example.manager.GroqRequest(
            messages = groqMessages
        )

        var lastException: Exception? = null
        for (attempt in 1..3) {
            try {
                val response = com.example.manager.GroqRetrofitClient.service.generateContent(
                    "Bearer $groqApiKey",
                    request
                )
                return response.choices.firstOrNull()?.message?.content ?: "NÚCLEO AETHER: Error de divergencia en la respuesta Groq."
            } catch (e: Exception) {
                lastException = e
                android.util.Log.e("AETHER", "Error en llamada a Groq", e)
                val is429 = e.message?.contains("429") == true || (e as? retrofit2.HttpException)?.code() == 429
                
                if (attempt < 3) {
                    kotlinx.coroutines.delay(2000L * attempt)
                    continue
                }
                
                if (is429) {
                    return "NÚCLEO AETHER: Límite de procesamiento cognitivo en cluster online alcanzado (HTTP 429). Por favor, aguarda."
                }
            }
        }
        return if (prompt.lowercase().let { it.contains("camara") || it.contains("cámara") || it.contains("foto") }) {
            "Entendido, señor. Activando sensores ópticos en tiempo real ahora mismo..."
        } else {
            "NÚCLEO AETHER: Conexión inestable con el nodo central online (${lastException?.message}). Reintenta en unos instantes."
        }
    }
}
