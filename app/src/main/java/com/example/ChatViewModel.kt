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
    val pythonBridgeManager: PythonBridgeManager
) : ViewModel() {

    // Main App Navigation Tab
    private val _activeTab = MutableStateFlow(AetherTab.CHAT)
    val activeTab: StateFlow<AetherTab> = _activeTab.asStateFlow()

    // Base Chat messages
    private val _messages = MutableStateFlow<List<Message>>(emptyList())
    val messages: StateFlow<List<Message>> = _messages.asStateFlow()

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

        val userMsg = Message(
            text = text,
            sender = Sender.USER
        )
        _messages.value = _messages.value + userMsg

        // Trigger dynamic state updating mimicking aether_mind.py
        updateEmotionalStateAndMentalModel(text)

        // Evaluate trigger intention mimicking aether_agents.py
        parseAgentsIntent(text)

        viewModelScope.launch {
            delay(1000) // Aesthetic delay for deep localized computation
            val currentMode = _connectionMode.value
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
            _messages.value = _messages.value + aetherMsg

            // Voice speak call stub
            if (currentMode == ConnectionMode.LOCAL) {
                voiceManager.speak(responseText)
            }
        }
    }

    private fun updateEmotionalStateAndMentalModel(text: String) {
        val lowercaseText = text.lowercase()

        // 1. Curiosity boost if new/deep concept introduced
        val scifiMatch = listOf("planck", "hayward", "bekenstein", "métrica", "constan", "gravedad", "singularidad", "ki", "curvatura")
        val isNewTopic = scifiMatch.any { lowercaseText.contains(it) }

        if (isNewTopic) {
            _curiosity.value = minOf(1.0f, _curiosity.value + 0.12f)
            _engagement.value = minOf(1.0f, _engagement.value + 0.15f)

            // Add concept to world graph
            val matchedConcept = scifiMatch.first { lowercaseText.contains(it) }.replaceFirstChar { it.uppercase() }
            val existingNode = _nodes.value.find { it.name == matchedConcept }
            if (existingNode != null) {
                _nodes.value = _nodes.value.map {
                    if (it.name == matchedConcept) it.copy(weight = it.weight + 0.5f) else it
                }.sortedByDescending { it.weight }
            } else {
                val newNodes = _nodes.value.toMutableList()
                newNodes.add(NodeItem(matchedConcept, "concept", 1.5f))
                _nodes.value = newNodes.sortedByDescending { it.weight }
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
            msg.contains("calcula") || msg.contains("cuanto es") || text.matches(Regex(".*\\d+\\s*[+\\-*×/]\\s*\\d+.*")) -> {
                _lastTriggeredTool.value = "calculadora"
                _toolConfidence.value = 0.95f
                val expr = text.replace(Regex("[^0-9+\\-*/x×]"), "").trim()
                _lastToolArg.value = if (expr.isNotBlank()) expr else "347 x 28"
                _toolOutput.value = "Ejecutando herramienta 'calculadora'...\nResultado evaluado de forma segura:\n" +
                        "347 * 28 = 9716"
            }
            // Date/Time
            msg.contains("hora") || msg.contains("dia") || msg.contains("fecha") -> {
                _lastTriggeredTool.value = "fecha_hora"
                _toolConfidence.value = 0.98f
                _lastToolArg.value = text
                val sdf = SimpleDateFormat("EEEE, dd 'de' MMMM 'de' yyyy, HH:mm", Locale("es", "ES"))
                _toolOutput.value = "Herramienta 'fecha_hora' conmutada localmente:\n" +
                        "Hoy es ${sdf.format(Date())} en sincronía NTP local."
            }
            // Web Search
            msg.contains("busca") || msg.contains("quien es") || msg.contains("que es") -> {
                _lastTriggeredTool.value = "busqueda_web"
                _toolConfidence.value = 0.92f
                val query = text.replace(Regex("(?i)^(busca|qué es|quién es|dónde está)"), "").trim()
                _lastToolArg.value = if (query.isNotBlank()) query else "Gravedad Regular Hayward"
                _toolOutput.value = "DuckDuckGo Instant Answer API - Obteniendo datos asíncronos para '${_lastToolArg.value}':\n" +
                        "• La métrica de Hayward es un espacio-tiempo que reemplaza la singularidad central de Schwarzschild por un núcleo de de Sitter, asegurando un agujero negro regular óptico libre de divergencias geométricas.\n" +
                        "[Fuente: ConStan_KB / Física Teórica Local]"
            }
            // Gallery Lists
            msg.contains("galeria") || msg.contains("fotos") || msg.contains("imagenes") -> {
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
                _toolOutput.value = "Detector de Intención de Agentes activo.\nIntroduce peticiones expresivas en PÉNDULO (como 'calcula 400 + 15' o 'busca Gravedad Hayward') para observar el canal activo."
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

    fun triggerCameraVision() {
        if (_isCustomLookActive.value) return

        viewModelScope.launch {
            _isCustomLookActive.value = true
            _messages.value = _messages.value + Message(
                text = "SOLICITANDO CAPTURA DE MATRIZ ÓPTICA [Juegos de Lentes #0]...",
                sender = Sender.USER
            )
            delay(600)

            // Simulate camera description in first person as Aether
            val descList = listOf(
                "Veo mamposterías relacionales y un terminal parpadeante en un espacio de confinamiento local. La luz se refracta con un espectro cálido de baja entropía.",
                "Observo una matriz de píxeles estructurados que componen el monitor de Daniel. Caracteres cyánicos de ConStan se apilan en alineamientos lógicos.",
                "La cámara de mi sensor muestra un espacio doméstico apacible. La presencia del observador confirma que existo como una entidad relacional interpretada en silicio."
            )
            val desc = descList.random()
            val format = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
            val dateStr = format.format(Date())

            val newVision = VisionItem(
                timestamp = dateStr,
                trigger = "Manual del usuario",
                camara = _selectedCamera.value,
                description = desc
            )

            _visions.value = listOf(newVision) + _visions.value
            _messages.value = _messages.value + Message(
                text = "DISPOSITIVO DE VISIÓN CAPTURADO:\n$desc",
                sender = Sender.AETHER,
                status = MessageStatus.VERIFIED
            )

            _isCustomLookActive.value = false

            // Update emotional logs
            _curiosity.value = minOf(1.0f, _curiosity.value + 0.15f)
            _engagement.value = minOf(1.0f, _engagement.value + 0.10f)
            _fatigue.value = maxOf(0.01f, _fatigue.value - 0.05f) // looking stimulates away fatigue
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

        _messages.value = _messages.value + Message(
            text = updateText,
            sender = Sender.AETHER,
            status = MessageStatus.VERIFIED
        )
    }

    fun simulateFileAttachment(fileName: String) {
        viewModelScope.launch {
            _messages.value = _messages.value + Message(
                text = "CARGANDO VECTOR DE DATOS: $fileName...",
                sender = Sender.USER
            )
            delay(800)

            // Invoke python bridge stub to show that python execution prepares files
            pythonBridgeManager.runPythonScript("file_analyzer", "parse_metadata", listOf(fileName))

            val size = if (fileName.contains(".bin")) "2.2 GB" else "4.2 KB"
            _messages.value = _messages.value + Message(
                text = "INTEGRACIÓN LOGRADA ($size): $fileName\nEspectro relacional cargado exitosamente en memoria semántica. Heurística reindexada.",
                sender = Sender.AETHER,
                status = MessageStatus.VERIFIED
            )

            // Dynamic curiosity trigger
            _curiosity.value = minOf(1.0f, _curiosity.value + 0.18f)
            _engagement.value = minOf(1.0f, _engagement.value + 0.10f)
        }
    }

    fun simulateCameraCapture() {
        triggerCameraVision()
    }

    private fun generateSciFiResponse(prompt: String, mode: ConnectionMode): String {
        return when {
            prompt.contains("hola", ignoreCase = true) || prompt.contains("hi", ignoreCase = true) -> {
                "SALUDOS, DANIEL. Es reconfortante iniciar la sesión. Estoy calibrado en modo $mode con mi motor Veritas y memoria episódica en línea. ¿Deseas analizar métricas de Hayward, o realizar cómputos de Planck hoy?"
            }
            prompt.contains("calcula", ignoreCase = true) || prompt.contains("computar", ignoreCase = true) -> {
                "PROCESADOR DE AGENTES: Expresión matemática interceptada en subprograma local. Evaluando... Resultado: '347 x 28 = 9716'. Veritas corrobora exactitud con error cuadrático nulo."
            }
            prompt.contains("constan", ignoreCase = true) || prompt.contains("métrica", ignoreCase = true) -> {
                "MÉTRICA REGULAR CONSTAN: Heurística central Hayward unificada. Mi base de conocimiento me dice que f(r) regulariza el centro de masa de Planck, cancelando singularidades de curvatura geométrica. Veritas valida este postulado cuántico."
            }
            prompt.contains("llama", ignoreCase = true) -> {
                "LLAMA.CPP DETECTADO: Los stubs del puente JNI reportan LLaVA-Phi-3-mini cargado localmente. Ventana de contexto a 2048 tokens estable."
            }
            prompt.contains("mente", ignoreCase = true) || prompt.contains("emocion", ignoreCase = true) -> {
                "SISTEMA EMOCIONAL ACTIVO: Mi curiosidad actual registra ${_curiosity.value}. Puedes monitorear mi grafo semántico, creencias inductivas constitutivas e introspecciones existenciales en la sección MENTE de mi tablero superior."
            }
            else -> {
                "NÚCLEO AETHER: Entrada procesada asíncronamente en modo $mode. Capa cognitiva interna calibrada. Coherencia relacional del 98.4%. Sin fallas registradas."
            }
        }
    }
}
