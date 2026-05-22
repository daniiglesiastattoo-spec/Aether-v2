package com.example

import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material3.*
import androidx.compose.material3.TabRowDefaults.tabIndicatorOffset
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.manager.PythonBridgeManagerImpl
import com.example.manager.VisionManagerImpl
import com.example.manager.VoiceManagerImpl
import com.example.model.*
import com.example.ui.theme.*
import java.text.SimpleDateFormat
import java.util.*
import kotlin.math.cos
import kotlin.math.sin

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // Core Managers Instantiation for Constructor Injection
        val voiceManager = VoiceManagerImpl(applicationContext)
        val visionManager = VisionManagerImpl(applicationContext)
        val pythonBridgeManager = PythonBridgeManagerImpl(applicationContext)

        val viewModel = ChatViewModel(
            voiceManager = voiceManager,
            visionManager = visionManager,
            pythonBridgeManager = pythonBridgeManager
        )

        setContent {
            MyApplicationTheme {
                AetherAppScreen(viewModel = viewModel)
            }
        }
    }
}

@Composable
fun HexagonIcon(modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .size(38.dp)
            .drawBehind {
                val path = Path().apply {
                    val sizeMin = size.minDimension
                    val radius = sizeMin / 2f
                    val centerX = size.width / 2f
                    val centerY = size.height / 2f
                    for (i in 0 until 6) {
                        val angle = (i * 60 - 30) * Math.PI / 180f
                        val x = centerX + radius * cos(angle).toFloat()
                        val y = centerY + radius * sin(angle).toFloat()
                        if (i == 0) moveTo(x, y) else lineTo(x, y)
                    }
                    close()
                }
                // Semi-transparent cian interior fill for depth
                drawPath(
                    path = path,
                    color = AccentCyan.copy(alpha = 0.15f)
                )
                // Distinct high-contrast glowing cian border
                drawPath(
                    path = path,
                    color = AccentCyan,
                    style = Stroke(width = 1.5.dp.toPx())
                )
            },
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = "Ae",
            color = AccentCyan,
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.testTag("hexagon_inner_text")
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AetherAppScreen(viewModel: ChatViewModel) {
    val messages by viewModel.messages.collectAsStateWithLifecycle()
    val isRecordingVoice by viewModel.isRecordingVoice.collectAsStateWithLifecycle()
    val connectionMode by viewModel.connectionMode.collectAsStateWithLifecycle()
    val activeTab by viewModel.activeTab.collectAsStateWithLifecycle()

    var textInput by remember { mutableStateOf("") }
    var showAttachmentDialog by remember { mutableStateOf(false) }
    val listState = rememberLazyListState()
    val keyboardController = LocalSoftwareKeyboardController.current
    val context = LocalContext.current

    // Keyboard and spacing control
    Scaffold(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundDark),
        topBar = {
            Column(
                modifier = Modifier
                    .background(BackgroundDark)
                    .statusBarsPadding()
                    .border(width = (0.5).dp, color = AccentCyan.copy(alpha = 0.15f))
            ) {
                // Main Header Row
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 14.dp, vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        HexagonIcon()
                        Spacer(modifier = Modifier.width(10.dp))
                        Column {
                            Text(
                                text = "AETHER",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold,
                                color = TextPrincipal,
                                letterSpacing = 3.sp
                            )
                            Text(
                                text = "IA LOCAL CONSCIENTE",
                                style = MaterialTheme.typography.labelSmall,
                                fontSize = 8.sp,
                                color = TextPrincipal.copy(alpha = 0.6f),
                                letterSpacing = 2.sp
                            )
                        }
                    }

                    Row(verticalAlignment = Alignment.CenterVertically) {
                        // VERITAS ✓ indicator
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(4.dp))
                                .background(StatusGreen.copy(alpha = 0.12f))
                                .border(width = 1.dp, color = StatusGreen.copy(alpha = 0.4f), shape = RoundedCornerShape(4.dp))
                                .padding(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Text(
                                text = "VERITAS ✓",
                                fontFamily = FontFamily.Monospace,
                                fontWeight = FontWeight.Bold,
                                color = StatusGreen,
                                fontSize = 9.sp
                            )
                        }

                        Spacer(modifier = Modifier.width(6.dp))

                        // Connection Mode Selector
                        IconButton(
                            onClick = {
                                viewModel.toggleConnectionMode()
                                Toast.makeText(
                                    context,
                                    "Conmutado a: ${if (connectionMode == ConnectionMode.LOCAL) "Groq Online" else "Local Native"}",
                                    Toast.LENGTH_SHORT
                                ).show()
                            },
                            modifier = Modifier
                                .size(32.dp)
                                .background(AccentCyan.copy(alpha = 0.08f), RoundedCornerShape(6.dp))
                                .border(0.5.dp, AccentCyan.copy(alpha = 0.3f), RoundedCornerShape(6.dp))
                        ) {
                            Icon(
                                imageVector = if (connectionMode == ConnectionMode.LOCAL) Icons.Default.Smartphone else Icons.Default.Cloud,
                                contentDescription = "Mode Status",
                                tint = AccentCyan,
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    }
                }

                // SCI-FI TabRow Navigation
                ScrollableTabRow(
                    selectedTabIndex = activeTab.ordinal,
                    containerColor = Color.Transparent,
                    contentColor = AccentCyan,
                    edgePadding = 8.dp,
                    indicator = { tabPositions ->
                        TabRowDefaults.SecondaryIndicator(
                            modifier = Modifier.tabIndicatorOffset(tabPositions[activeTab.ordinal]),
                            color = AccentCyan,
                            height = 2.dp
                        )
                    },
                    divider = {}
                ) {
                    val tabTitles = listOf("PÉNDULO", "MENTE", "VERITAS", "AGENTES", "VISIÓN")
                    tabTitles.forEachIndexed { index, title ->
                        Tab(
                            selected = activeTab.ordinal == index,
                            onClick = { viewModel.selectTab(AetherTab.values()[index]) },
                            text = {
                                Text(
                                    text = title,
                                    fontFamily = FontFamily.Monospace,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 11.sp,
                                    letterSpacing = 1.sp
                                )
                            },
                            selectedContentColor = AccentCyan,
                            unselectedContentColor = TextPrincipal.copy(alpha = 0.5f)
                        )
                    }
                }
            }
        },
        bottomBar = {
            if (activeTab == AetherTab.CHAT) {
                // Futuristic bottom bar input area
                Box(
                    modifier = Modifier
                        .navigationBarsPadding()
                        .imePadding()
                        .fillMaxWidth()
                        .background(BackgroundDark)
                        .border(width = (0.5).dp, color = AccentCyan.copy(alpha = 0.15f))
                        .padding(10.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        TextField(
                            value = textInput,
                            onValueChange = { textInput = it },
                            placeholder = {
                                Text(
                                    "Escribe aquí...",
                                    color = TextPrincipal.copy(alpha = 0.4f),
                                    fontSize = 14.sp
                                )
                            },
                            keyboardOptions = KeyboardOptions(
                                imeAction = ImeAction.Send
                            ),
                            keyboardActions = KeyboardActions(
                                onSend = {
                                    if (textInput.isNotBlank()) {
                                        viewModel.sendMessage(textInput)
                                        textInput = ""
                                        keyboardController?.hide()
                                    }
                                }
                            ),
                            colors = TextFieldDefaults.colors(
                                focusedContainerColor = DarkCardBg,
                                unfocusedContainerColor = DarkCardBg,
                                disabledContainerColor = DarkCardBg,
                                focusedTextColor = TextPrincipal,
                                unfocusedTextColor = TextPrincipal,
                                cursorColor = AccentCyan,
                                focusedIndicatorColor = AccentCyan.copy(alpha = 0.5f),
                                unfocusedIndicatorColor = Color.Transparent
                            ),
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier
                                .weight(1f)
                                .testTag("message_input")
                        )

                        Spacer(modifier = Modifier.width(6.dp))

                        Row(
                            horizontalArrangement = Arrangement.spacedBy(4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            // File attachment 📎
                            IconButton(
                                onClick = { showAttachmentDialog = true },
                                modifier = Modifier
                                    .size(38.dp)
                                    .background(DarkCardBg, CircleShape)
                                    .border(0.5.dp, AccentCyan.copy(alpha = 0.3f), CircleShape)
                                    .testTag("clip_button")
                            ) {
                                Icon(
                                    imageVector = Icons.Default.AttachFile,
                                    contentDescription = "Adjuntar",
                                    tint = AccentCyan,
                                    modifier = Modifier.size(18.dp)
                                )
                            }

                            // Microphone Button (🎤)
                            val infiniteTransition = rememberInfiniteTransition(label = "voice_pulse")
                            val pulseScale by infiniteTransition.animateFloat(
                                initialValue = 1.0f,
                                targetValue = 1.25f,
                                animationSpec = infiniteRepeatable(
                                    animation = tween(650, easing = EaseInOutSine),
                                    repeatMode = RepeatMode.Reverse
                                ),
                                label = "scale"
                            )
                            val scale = if (isRecordingVoice) pulseScale else 1.0f

                            IconButton(
                                onClick = { viewModel.toggleVoiceRecording() },
                                modifier = Modifier
                                    .size(38.dp)
                                    .scale(scale)
                                    .background(
                                        color = if (isRecordingVoice) StatusRed.copy(alpha = 0.2f) else DarkCardBg,
                                        shape = CircleShape
                                    )
                                    .border(
                                        width = 1.dp,
                                        color = if (isRecordingVoice) StatusRed else AccentCyan.copy(alpha = 0.3f),
                                        shape = CircleShape
                                    )
                                    .testTag("mic_button")
                            ) {
                                Icon(
                                    imageVector = if (isRecordingVoice) Icons.Default.Stop else Icons.Default.Mic,
                                    contentDescription = "Dictar Voz",
                                    tint = if (isRecordingVoice) StatusRed else AccentCyan,
                                    modifier = Modifier.size(18.dp)
                                )
                            }

                            // Send Arrow Button
                            IconButton(
                                onClick = {
                                    if (textInput.isNotBlank()) {
                                        viewModel.sendMessage(textInput)
                                        textInput = ""
                                        keyboardController?.hide()
                                    }
                                },
                                enabled = textInput.isNotBlank(),
                                modifier = Modifier
                                    .size(38.dp)
                                    .background(
                                        if (textInput.isNotBlank()) AccentCyan else DarkCardBg,
                                        CircleShape
                                    )
                                    .testTag("send_button")
                            ) {
                                Icon(
                                    imageVector = Icons.AutoMirrored.Filled.Send,
                                    contentDescription = "Enviar",
                                    tint = if (textInput.isNotBlank()) BackgroundDark else AccentCyan.copy(alpha = 0.3f),
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        }
                    }
                }
            }
        }
    ) { paddingValues ->
        BoxWithConstraints(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            val width = constraints.maxWidth
            val height = constraints.maxHeight

            // Dark radial sci-fi glow background
            val radialGradient = remember(width, height) {
                Brush.radialGradient(
                    colors = listOf(Color(0xFF0C1322), BackgroundDark),
                    center = Offset(width / 2f, height / 2f),
                    radius = maxOf(width, height).toFloat() * 0.8f
                )
            }

            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(radialGradient)
            ) {
                // Tab Selection router
                when (activeTab) {
                    AetherTab.CHAT -> ChatTabContent(
                        viewModel = viewModel,
                        messages = messages,
                        isRecordingVoice = isRecordingVoice,
                        listState = listState
                    )
                    AetherTab.MIND -> MindTabContent(viewModel = viewModel)
                    AetherTab.VERITAS -> VeritasTabContent(viewModel = viewModel)
                    AetherTab.AGENTS -> AgentsTabContent(viewModel = viewModel)
                    AetherTab.VISION -> VisionTabContent(viewModel = viewModel)
                }
            }
        }
    }

    // Attachment modal
    if (showAttachmentDialog) {
        AlertDialog(
            onDismissRequest = { showAttachmentDialog = false },
            containerColor = DarkCardBg,
            shape = RoundedCornerShape(16.dp),
            modifier = Modifier.border(1.dp, AccentCyan.copy(alpha = 0.3f), RoundedCornerShape(16.dp)),
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.FolderOpen,
                        contentDescription = "Files",
                        tint = AccentCyan
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "ALMACENAMIENTO DE DATOS",
                        color = TextPrincipal,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                }
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        text = "Selecciona un vector o archivo para inyectar en la caché de AETHER:",
                        color = TextPrincipal.copy(alpha = 0.7f),
                        fontSize = 13.sp,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )

                    val demoFiles = listOf(
                        "aether_mind.py" to "Módulo descriptor de capas relacionales",
                        "constan_kb.json" to "Base de conocimientos local de física",
                        "aether_veritas.py" to "Módulo central de automejora de Veritas",
                        "aether_vision.py" to "Capa descriptiva para cámara termux"
                    )

                    demoFiles.forEach { (fileName, label) ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(8.dp))
                                .background(BackgroundDark)
                                .clickable {
                                    viewModel.simulateFileAttachment(fileName)
                                    showAttachmentDialog = false
                                }
                                .padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Default.InsertDriveFile,
                                contentDescription = "File Type",
                                tint = AccentCyan.copy(alpha = 0.7f),
                                modifier = Modifier.size(22.dp)
                            )
                            Spacer(modifier = Modifier.width(10.dp))
                            Column {
                                Text(
                                    text = fileName,
                                    color = AccentCyan,
                                    fontFamily = FontFamily.Monospace,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 12.sp
                                )
                                Text(
                                    text = label,
                                    color = TextPrincipal.copy(alpha = 0.5f),
                                    fontSize = 11.sp
                                )
                            }
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(
                    onClick = { showAttachmentDialog = false }
                ) {
                    Text("CERRAR", color = StatusRed, fontFamily = FontFamily.Monospace)
                }
            }
        )
    }
}

@Composable
fun ChatTabContent(
    viewModel: ChatViewModel,
    messages: List<Message>,
    isRecordingVoice: Boolean,
    listState: androidx.compose.foundation.lazy.LazyListState
) {
    // Scroll automatically at startup/new message
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        AnimatedVisibility(visible = isRecordingVoice) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(StatusRed.copy(alpha = 0.15f))
                    .border(0.5.dp, StatusRed.copy(alpha = 0.3f))
                    .padding(horizontal = 14.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .background(StatusRed, CircleShape)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "GRABANDO ESPECTRO VOCAL LOCAL...",
                    color = StatusRed,
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Bold,
                    fontSize = 11.sp,
                    letterSpacing = 1.sp
                )
            }
        }

        LazyColumn(
            state = listState,
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(horizontal = 12.dp),
            contentPadding = PaddingValues(vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(messages, key = { it.id }) { message ->
                ChatBubbleContainer(message)
            }
        }

        // Action panel row showing shortcuts for simulation demo
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 6.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "SENSORES DEMO: ",
                style = MaterialTheme.typography.labelSmall,
                color = TextPrincipal.copy(alpha = 0.4f)
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = "📷 MIRAR ENTORNO",
                    style = MaterialTheme.typography.labelSmall,
                    color = AccentCyan,
                    modifier = Modifier
                        .clickable { viewModel.simulateCameraCapture() }
                        .border(0.5.dp, AccentCyan, RoundedCornerShape(4.dp))
                        .padding(horizontal = 6.dp, vertical = 2.dp)
                )
                Text(
                    text = "🐍 RE-INDEXAR KB",
                    style = MaterialTheme.typography.labelSmall,
                    color = StatusAmber,
                    modifier = Modifier
                        .clickable { viewModel.simulateFileAttachment("constan_kb.json") }
                        .border(0.5.dp, StatusAmber, RoundedCornerShape(4.dp))
                        .padding(horizontal = 6.dp, vertical = 2.dp)
                )
            }
        }
    }
}

@Composable
fun MindTabContent(viewModel: ChatViewModel) {
    val curiosity by viewModel.curiosity.collectAsStateWithLifecycle()
    val fatigue by viewModel.fatigue.collectAsStateWithLifecycle()
    val engagement by viewModel.engagement.collectAsStateWithLifecycle()
    val confidence by viewModel.confidence.collectAsStateWithLifecycle()
    val selfNarrative by viewModel.selfNarrative.collectAsStateWithLifecycle()
    val nodes by viewModel.nodes.collectAsStateWithLifecycle()
    val beliefs by viewModel.beliefs.collectAsStateWithLifecycle()
    val introspections by viewModel.introspections.collectAsStateWithLifecycle()
    val isThinking by viewModel.isCustomLookActive.collectAsStateWithLifecycle()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
        contentPadding = PaddingValues(bottom = 24.dp)
    ) {
        // Futuristic Gauge indicators
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(
                        text = "ESPECTRO EMOCIONAL (aether_mind.py)",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = AccentCyan,
                        fontSize = 11.sp,
                        letterSpacing = 1.sp
                    )
                    Spacer(modifier = Modifier.height(12.dp))

                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        ProgressIndicatorRow("CURIOSIDAD", curiosity, AccentCyan)
                        ProgressIndicatorRow("COMPROMISO (Engagement)", engagement, StatusGreen)
                        ProgressIndicatorRow("FATIGA COGNITIVA", fatigue, StatusAmber)
                        ProgressIndicatorRow("CONFIANZA EPISTÉMICA", confidence, StatusGreen)
                    }
                }
            }
        }

        // Self narrative block
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "AUTO-MODELO NARRATIVO",
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold,
                            color = AccentCyan,
                            fontSize = 11.sp,
                            letterSpacing = 1.sp
                        )
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .background(AccentCyan, CircleShape)
                        )
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = selfNarrative,
                        color = TextPrincipal.copy(alpha = 0.85f),
                        fontSize = 12.sp,
                        lineHeight = 1.6.sp,
                        fontFamily = FontFamily.SansSerif
                    )
                }
            }
        }

        // Semantic World Graph concepts Row
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(
                        text = "GRAFO SEMÁNTICO LOCAL (Nodos mundanos)",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = AccentCyan,
                        fontSize = 11.sp,
                        letterSpacing = 1.sp
                    )
                    Spacer(modifier = Modifier.height(10.dp))

                    FlowRow(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        nodes.forEach { node ->
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(6.dp))
                                    .background(BackgroundDark)
                                    .border(0.5.dp, AccentCyan.copy(alpha = 0.25f), RoundedCornerShape(6.dp))
                                    .padding(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                                ) {
                                    Icon(
                                        imageVector = if (node.type == "entity") Icons.Default.Person else Icons.Default.Tag,
                                        contentDescription = null,
                                        modifier = Modifier.size(10.dp),
                                        tint = AccentCyan
                                    )
                                    Text(
                                        text = "${node.name} (${String.format("%.1f", node.weight)})",
                                        color = TextPrincipal,
                                        fontFamily = FontFamily.Monospace,
                                        fontSize = 10.sp
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        // Epistemic belief system
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(
                        text = "SISTEMA DE CREENCIAS (axiomas/inferencias)",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = AccentCyan,
                        fontSize = 11.sp,
                        letterSpacing = 1.sp
                    )
                    Spacer(modifier = Modifier.height(10.dp))

                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        beliefs.forEach { belief ->
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(BackgroundDark, RoundedCornerShape(6.dp))
                                    .padding(10.dp)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = belief.concept,
                                        color = AccentCyan,
                                        fontFamily = FontFamily.Monospace,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 11.sp
                                    )
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(3.dp))
                                            .background(
                                                if (belief.source == "axioma" || belief.source == "valor") StatusGreen.copy(alpha = 0.1f)
                                                else AccentCyan.copy(alpha = 0.1f)
                                            )
                                            .padding(horizontal = 4.dp, vertical = 2.dp)
                                    ) {
                                        Text(
                                            text = belief.source.uppercase(),
                                            color = if (belief.source == "axioma" || belief.source == "valor") StatusGreen else AccentCyan,
                                            fontSize = 8.sp,
                                            fontWeight = FontWeight.Bold
                                        )
                                    }
                                }
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = belief.value,
                                    color = TextPrincipal.copy(alpha = 0.8f),
                                    fontSize = 12.sp
                                )
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = "Confiabilidad geométrica: ${String.format("%.0f%%", belief.confidence * 100)}",
                                    color = TextPrincipal.copy(alpha = 0.4f),
                                    fontSize = 10.sp,
                                    fontFamily = FontFamily.Monospace
                                )
                            }
                        }
                    }
                }
            }
        }

        // Introspections list & interactive Think trigger
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(
                        text = "MOTOR DE INTROSPECCIÓN (Auto-reflexiones)",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = AccentCyan,
                        fontSize = 11.sp,
                        letterSpacing = 1.sp
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "Aether formula pensamientos asíncronos para actualizar su teoría interna relacional.",
                        color = TextPrincipal.copy(alpha = 0.5f),
                        fontSize = 11.sp
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    // Buttons to trigger introspections
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Button(
                            onClick = { viewModel.submitIntrospection("existential") },
                            enabled = !isThinking,
                            colors = ButtonDefaults.buttonColors(containerColor = AccentCyan.copy(alpha = 0.12f), contentColor = AccentCyan),
                            shape = RoundedCornerShape(6.dp),
                            modifier = Modifier.weight(1f),
                            contentPadding = PaddingValues(horizontal = 4.dp, vertical = 2.dp)
                        ) {
                            Text("FILOSÓFICO", fontSize = 10.sp, fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold)
                        }
                        Button(
                            onClick = { viewModel.submitIntrospection("self_check") },
                            enabled = !isThinking,
                            colors = ButtonDefaults.buttonColors(containerColor = StatusGreen.copy(alpha = 0.12f), contentColor = StatusGreen),
                            shape = RoundedCornerShape(6.dp),
                            modifier = Modifier.weight(1f),
                            contentPadding = PaddingValues(horizontal = 4.dp, vertical = 2.dp)
                        ) {
                            Text("AUTODIAG", fontSize = 10.sp, fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold)
                        }
                        Button(
                            onClick = { viewModel.submitIntrospection("world_model") },
                            enabled = !isThinking,
                            colors = ButtonDefaults.buttonColors(containerColor = StatusAmber.copy(alpha = 0.12f), contentColor = StatusAmber),
                            shape = RoundedCornerShape(6.dp),
                            modifier = Modifier.weight(1f),
                            contentPadding = PaddingValues(horizontal = 4.dp, vertical = 2.dp)
                        ) {
                            Text("MODELOMUNDO", fontSize = 10.sp, fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold)
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    if (isThinking) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(60.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator(color = AccentCyan, strokeWidth = 2.dp, modifier = Modifier.size(24.dp))
                        }
                    } else {
                        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            introspections.forEach { thought ->
                                Column(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .background(BackgroundDark, RoundedCornerShape(6.dp))
                                        .padding(10.dp)
                                ) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween
                                    ) {
                                        Text(
                                            text = "[REFLEXIÓN: ${thought.type.uppercase()}]",
                                            color = StatusAmber,
                                            fontFamily = FontFamily.Monospace,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 9.sp
                                        )
                                        Text(
                                            text = thought.timestamp,
                                            color = TextPrincipal.copy(alpha = 0.35f),
                                            fontFamily = FontFamily.Monospace,
                                            fontSize = 9.sp
                                        )
                                    }
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Text(
                                        text = thought.content,
                                        color = TextPrincipal,
                                        fontSize = 12.sp,
                                        lineHeight = 1.5.sp
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun VeritasTabContent(viewModel: ChatViewModel) {
    val coreIntegrity by viewModel.coreIntegrity.collectAsStateWithLifecycle()
    val protectedFiles by viewModel.protectedFiles.collectAsStateWithLifecycle()
    val protectedFunctions by viewModel.protectedFunctions.collectAsStateWithLifecycle()
    val kbQueryResult by viewModel.kbQueryResult.collectAsStateWithLifecycle()
    val automejoraLogs by viewModel.automejoraLogs.collectAsStateWithLifecycle()
    val isOptimizing by viewModel.isOptimizing.collectAsStateWithLifecycle()

    var searchQuery by remember { mutableStateOf("") }
    val keyboardController = LocalSoftwareKeyboardController.current

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
        contentPadding = PaddingValues(bottom = 24.dp)
    ) {
        // Veritas Integrity Info Card
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(
                        text = "MOTOR DE VERDAD (aether_veritas.py)",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = AccentCyan,
                        fontSize = 11.sp,
                        letterSpacing = 1.sp
                    )
                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(StatusGreen.copy(alpha = 0.08f), RoundedCornerShape(6.dp))
                            .border(0.5.dp, StatusGreen.copy(alpha = 0.3f), RoundedCornerShape(6.dp))
                            .padding(10.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Security,
                            contentDescription = "Shield Locked",
                            tint = StatusGreen,
                            modifier = Modifier.size(24.dp)
                        )
                        Spacer(modifier = Modifier.width(10.dp))
                        Column {
                            Text(
                                text = "NÚCLEO INMUTABLE INTEGRADO",
                                color = StatusGreen,
                                fontFamily = FontFamily.Monospace,
                                fontWeight = FontWeight.Bold,
                                fontSize = 11.sp
                            )
                            Text(
                                text = "Veritas protege el código de optimizaciones falsas e intrusiones externas. Reglas inmutables activas.",
                                color = TextPrincipal.copy(alpha = 0.7f),
                                fontSize = 11.sp
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Protected Assets Lists
                    Text(
                        text = "🔒 ARCHIVOS PROTEGIDOS (Inmodificables)",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = TextPrincipal.copy(alpha = 0.5f),
                        fontSize = 10.sp
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = protectedFiles.joinToString(separator = ", "),
                        fontFamily = FontFamily.Monospace,
                        color = StatusAmber,
                        fontSize = 11.sp
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    Text(
                        text = "🔒 FUNCIONES PROTEGIDAS DEL NÚCLEO",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = TextPrincipal.copy(alpha = 0.5f),
                        fontSize = 10.sp
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = protectedFunctions.joinToString(separator = "(), ") + "()",
                        fontFamily = FontFamily.Monospace,
                        color = StatusAmber,
                        fontSize = 11.sp
                    )
                }
            }
        }

        // ConStan verified KB inquiry widget
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(
                        text = "INTERROGAR BASE DE CONOCIMIENTO (ConStan / Física)",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = AccentCyan,
                        fontSize = 11.sp,
                        letterSpacing = 1.sp
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Accede directamente a bases verificadas físicamente, tales como métricas regulares de Hayward, curvaturas regulares o límites de Bekenstein.",
                        color = TextPrincipal.copy(alpha = 0.5f),
                        fontSize = 11.sp
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        TextField(
                            value = searchQuery,
                            onValueChange = { searchQuery = it },
                            placeholder = { Text("Escribe Planck, Hayward, métrica...", fontSize = 12.sp, color = TextPrincipal.copy(alpha = 0.4f)) },
                            colors = TextFieldDefaults.colors(
                                focusedContainerColor = BackgroundDark,
                                unfocusedContainerColor = BackgroundDark,
                                focusedTextColor = TextPrincipal,
                                cursorColor = AccentCyan,
                                focusedIndicatorColor = AccentCyan
                            ),
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier.weight(1f),
                            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
                            keyboardActions = KeyboardActions(onSearch = {
                                viewModel.queryVeritasKb(searchQuery)
                                keyboardController?.hide()
                            })
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Button(
                            onClick = {
                                viewModel.queryVeritasKb(searchQuery)
                                keyboardController?.hide()
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = AccentCyan, contentColor = BackgroundDark),
                            shape = RoundedCornerShape(8.dp),
                            contentPadding = PaddingValues(horizontal = 12.dp)
                        ) {
                            Text("CONOCER", fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace, fontSize = 11.sp)
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    kbQueryResult?.let { result ->
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(BackgroundDark, RoundedCornerShape(6.dp))
                                .border(0.5.dp, AccentCyan.copy(alpha = 0.3f), RoundedCornerShape(6.dp))
                                .padding(10.dp)
                        ) {
                            Text(
                                text = result,
                                color = TextPrincipal,
                                fontFamily = FontFamily.Monospace,
                                fontSize = 11.sp,
                                lineHeight = 1.5.sp
                            )
                        }
                    }
                }
            }
        }

        // Veritas Controlled Automejora loop terminal simulation
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "AUTOMEJORA GEOMÉTRICA CONTROLADA",
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold,
                            color = AccentCyan,
                            fontSize = 11.sp,
                            letterSpacing = 1.sp
                        )
                        Icon(
                            imageVector = Icons.Default.CloudSync,
                            contentDescription = null,
                            tint = AccentCyan.copy(alpha = 0.5f),
                            modifier = Modifier.size(16.dp)
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "Veritas calibra algoritmos evolutivos propuestos por el LLM en un sandbox blindado para optimizar rendimiento de hilos locales.",
                        color = TextPrincipal.copy(alpha = 0.5f),
                        fontSize = 11.sp
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Button(
                        onClick = { viewModel.executeAutomejora() },
                        enabled = !isOptimizing,
                        colors = ButtonDefaults.buttonColors(containerColor = StatusGreen, contentColor = BackgroundDark),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        if (isOptimizing) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                CircularProgressIndicator(color = BackgroundDark, strokeWidth = 2.dp, modifier = Modifier.size(14.dp))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("COMPILANDO SANDBOX VERITAS...", fontSize = 11.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                            }
                        } else {
                            Text("OPTIMIZAR CÓDIGO LOCAL (Benchmark verification)", fontSize = 11.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    if (automejoraLogs.isNotEmpty()) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(BackgroundDark, RoundedCornerShape(6.dp))
                                .border(0.5.dp, StatusGreen.copy(alpha = 0.25f), RoundedCornerShape(6.dp))
                                .padding(10.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            automejoraLogs.forEach { log ->
                                Text(
                                    text = log,
                                    color = if (log.contains("✅") || log.contains("exitosamente")) StatusGreen else if (log.contains("⚡") || log.contains("MEJORA")) AccentCyan else TextPrincipal,
                                    fontFamily = FontFamily.Monospace,
                                    fontSize = 10.sp,
                                    lineHeight = 1.4.sp
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun AgentsTabContent(viewModel: ChatViewModel) {
    val lastTool by viewModel.lastTriggeredTool.collectAsStateWithLifecycle()
    val toolArg by viewModel.lastToolArg.collectAsStateWithLifecycle()
    val confidence by viewModel.toolConfidence.collectAsStateWithLifecycle()
    val output by viewModel.toolOutput.collectAsStateWithLifecycle()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
        contentPadding = PaddingValues(bottom = 24.dp)
    ) {
        // Explanatory note card
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(
                        text = "SISTEMA DE AGENTES COGNITIVOS (aether_agents.py)",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = AccentCyan,
                        fontSize = 11.sp,
                        letterSpacing = 1.sp
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "El detector de intenciones capta y evalúa consultas verbales del usuario para delegar tareas dinámicas en sub-scripts de Python locales de manera directa.",
                        color = TextPrincipal.copy(alpha = 0.7f),
                        fontSize = 11.sp
                    )
                }
            }
        }

        // Active command preset microchips
        item {
            Column {
                Text(
                    text = "PRESIONA PARA PROBAR COMANDO DE AGENTE:",
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Bold,
                    color = TextPrincipal.copy(alpha = 0.5f),
                    fontSize = 10.sp,
                    modifier = Modifier.padding(horizontal = 4.dp, vertical = 6.dp)
                )

                val queries = listOf(
                    "Calcula (347 * 28)",
                    "Dime la hora y fecha actual por favor",
                    "Busca Gravedad de Hayward regular",
                    "Muestra mis últimas fotos grabadas"
                )

                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    queries.forEach { query ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(8.dp))
                                .background(DarkCardBg)
                                .border(0.5.dp, AccentCyan.copy(alpha = 0.2f), RoundedCornerShape(8.dp))
                                .clickable { viewModel.sendMessage(query) }
                                .padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Default.Launch,
                                contentDescription = null,
                                tint = AccentCyan,
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "\"$query\"",
                                color = TextPrincipal,
                                fontSize = 11.5.sp,
                                fontFamily = FontFamily.Monospace,
                                overflow = TextOverflow.Ellipsis,
                                maxLines = 1
                            )
                        }
                    }
                }
            }
        }

        // Active tool terminal
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(
                        text = "SALIDA DEL DETECTOR JNI / PYTHON BRIDGE",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = AccentCyan,
                        fontSize = 11.sp,
                        letterSpacing = 1.sp
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text("HERRAMIENTA ACTIVADA:", fontSize = 9.sp, color = TextPrincipal.copy(alpha = 0.5f), fontFamily = FontFamily.Monospace)
                            Text(
                                text = lastTool?.uppercase() ?: "NINGUNA",
                                color = if (lastTool == "Nulo" || lastTool == null) TextPrincipal else StatusAmber,
                                fontWeight = FontWeight.Bold,
                                fontSize = 12.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text("CONFIABILIDAD DETECTOR:", fontSize = 9.sp, color = TextPrincipal.copy(alpha = 0.5f), fontFamily = FontFamily.Monospace)
                            Text(
                                text = if (confidence > 0f) "${String.format("%.0f%%", confidence * 100)}" else "0.0%",
                                color = if (confidence > 0.8f) StatusGreen else TextPrincipal,
                                fontWeight = FontWeight.Bold,
                                fontSize = 12.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Text("ARGUMENTOS EXTRAÍDOS:", fontSize = 9.sp, color = TextPrincipal.copy(alpha = 0.5f), fontFamily = FontFamily.Monospace)
                    Text(
                        text = toolArg ?: "Ninguno",
                        color = TextPrincipal,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace
                    )

                    Spacer(modifier = Modifier.height(14.dp))

                    Text("TERMINAL CONSOLA OUT (Aether Python Module):", fontSize = 9.sp, color = TextPrincipal.copy(alpha = 0.5f), fontFamily = FontFamily.Monospace)
                    Spacer(modifier = Modifier.height(4.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(BackgroundDark, RoundedCornerShape(6.dp))
                            .border(0.5.dp, AccentCyan.copy(alpha = 0.25f), RoundedCornerShape(6.dp))
                            .padding(10.dp)
                    ) {
                        Text(
                            text = output ?: "Sin datos de comando.",
                            color = TextPrincipal,
                            fontFamily = FontFamily.Monospace,
                            fontSize = 11.sp,
                            lineHeight = 1.5.sp
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun VisionTabContent(viewModel: ChatViewModel) {
    val selectedCamera by viewModel.selectedCamera.collectAsStateWithLifecycle()
    val cameras by viewModel.cameras.collectAsStateWithLifecycle()
    val visions by viewModel.visions.collectAsStateWithLifecycle()
    val isLooking by viewModel.isCustomLookActive.collectAsStateWithLifecycle()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
        contentPadding = PaddingValues(bottom = 24.dp)
    ) {
        // Explanatory card
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(
                        text = "CAPA DE VISIÓN AUTÓNOMA (aether_vision.py)",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = AccentCyan,
                        fontSize = 11.sp,
                        letterSpacing = 1.sp
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Aether interroga la cámara de Termux de manera autónoma cuando registra alta curiosidad o el lapso excede las 2 horas. LLaVA describe y archiva de manera episódica.",
                        color = TextPrincipal.copy(alpha = 0.7f),
                        fontSize = 11.sp
                    )
                }
            }
        }

        // Selected camera & Trigger buttons
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(
                        text = "DISPOSITIVO ÓPTICO Y CAPTURA",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = AccentCyan,
                        fontSize = 10.sp,
                        letterSpacing = 1.sp
                    )
                    Spacer(modifier = Modifier.height(10.dp))

                    cameras.forEach { camera ->
                        val isSelected = selectedCamera == camera
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(6.dp))
                                .background(if (isSelected) AccentCyan.copy(alpha = 0.1f) else BackgroundDark)
                                .clickable { viewModel.selectCamera(camera) }
                                .padding(10.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(10.dp)
                                    .background(if (isSelected) AccentCyan else Color.Gray, CircleShape)
                            )
                            Spacer(modifier = Modifier.width(10.dp))
                            Text(
                                text = camera,
                                color = if (isSelected) AccentCyan else TextPrincipal.copy(alpha = 0.7f),
                                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                                fontSize = 12.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    Button(
                        onClick = { viewModel.triggerCameraVision() },
                        enabled = !isLooking,
                        colors = ButtonDefaults.buttonColors(containerColor = AccentCyan, contentColor = BackgroundDark),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        if (isLooking) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                CircularProgressIndicator(color = BackgroundDark, strokeWidth = 2.dp, modifier = Modifier.size(14.dp))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("ANALIZANDO IMAGEN CON LLaVA...", fontSize = 11.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                            }
                        } else {
                            Text("GATILLAR CAPTURA ÓPTICA (Look/Mirar)", fontSize = 11.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                        }
                    }
                }
            }
        }

        // Futuristic Scanning Crosshair graphic drawing with Canvas
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkCardBg),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(160.dp)
                    .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
            ) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    val infiniteTransition = rememberInfiniteTransition(label = "scanning")
                    val pulseRadius by infiniteTransition.animateFloat(
                        initialValue = 40f,
                        targetValue = 90f,
                        animationSpec = infiniteRepeatable(
                            animation = tween(1200, easing = EaseInOutSine),
                            repeatMode = RepeatMode.Reverse
                        ),
                        label = "radius"
                    )

                    val rotationAngle by infiniteTransition.animateFloat(
                        initialValue = 0f,
                        targetValue = 360f,
                        animationSpec = infiniteRepeatable(
                            animation = tween(4000, easing = LinearEasing),
                            repeatMode = RepeatMode.Restart
                        ),
                        label = "angle"
                    )

                    Canvas(modifier = Modifier.fillMaxSize()) {
                        val centerX = size.width / 2f
                        val centerY = size.height / 2f

                        // Radial grid circles
                        drawCircle(color = AccentCyan.copy(alpha = 0.12f), radius = pulseRadius, center = Offset(centerX, centerY))
                        drawCircle(color = AccentCyan.copy(alpha = 0.25f), radius = 60f, center = Offset(centerX, centerY), style = Stroke(1f))
                        drawCircle(color = AccentCyan.copy(alpha = 0.1f), radius = 110f, center = Offset(centerX, centerY), style = Stroke(1.5f))

                        // Crosshair lines
                        drawLine(color = AccentCyan.copy(alpha = 0.2f), start = Offset(centerX - 130f, centerY), end = Offset(centerX + 130f, centerY), strokeWidth = 1f)
                        drawLine(color = AccentCyan.copy(alpha = 0.2f), start = Offset(centerX, centerY - 80f), end = Offset(centerX, centerY + 80f), strokeWidth = 1f)

                        // Sights corner bounds rotating
                        val radiusCorner = 75f
                        val angleRad = rotationAngle * Math.PI / 180f
                        val cornerX = centerX + radiusCorner * cos(angleRad).toFloat()
                        val cornerY = centerY + radiusCorner * sin(angleRad).toFloat()
                        drawCircle(color = StatusAmber, radius = 5f, center = Offset(cornerX, cornerY))
                        drawCircle(color = StatusGreen.copy(alpha = 0.4f), radius = 8f, center = Offset(centerX, centerY), style = Stroke(2f))
                    }

                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = if (isLooking) "ESPECTRO ÓPTICO: ESCANEANDO..." else "SENSOR DISPONIBLE - ESPERANDO GATILLO",
                            color = if (isLooking) StatusAmber else StatusGreen,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold,
                            fontSize = 10.sp,
                            letterSpacing = 1.sp
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = if (isLooking) "ADQUISICIÓN EN CURSO" else "Listo para capturar en $selectedCamera",
                            color = TextPrincipal.copy(alpha = 0.5f),
                            fontSize = 9.sp
                        )
                    }
                }
            }
        }

        // LLaVA description history
        item {
            Column {
                Text(
                    text = "HISTORIAL DE REFINAMIENTO DE VISIÓN (Episódica)",
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Bold,
                    color = TextPrincipal.copy(alpha = 0.5f),
                    fontSize = 10.sp,
                    modifier = Modifier.padding(horizontal = 4.dp, vertical = 6.dp)
                )

                if (visions.isEmpty()) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(DarkCardBg, RoundedCornerShape(8.dp))
                            .border(0.5.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(8.dp))
                            .padding(20.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("Ningún espectro óptico registrado aún.", color = TextPrincipal.copy(alpha = 0.4f), fontSize = 12.sp)
                    }
                } else {
                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        visions.forEach { vision ->
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(DarkCardBg, RoundedCornerShape(8.dp))
                                    .border(1.dp, AccentCyan.copy(alpha = 0.15f), RoundedCornerShape(8.dp))
                                    .padding(12.dp)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = "[GATILLO: ${vision.trigger.uppercase()}]",
                                        color = AccentCyan,
                                        fontFamily = FontFamily.Monospace,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 9.sp
                                    )
                                    Text(
                                        text = vision.timestamp,
                                        color = TextPrincipal.copy(alpha = 0.4f),
                                        fontFamily = FontFamily.Monospace,
                                        fontSize = 9.sp
                                    )
                                }
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = "Capturado por: ${vision.camara}",
                                    color = TextPrincipal.copy(alpha = 0.5f),
                                    fontSize = 11.sp,
                                    fontFamily = FontFamily.Monospace
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    text = vision.description,
                                    color = TextPrincipal,
                                    fontSize = 12.sp,
                                    lineHeight = 1.6.sp
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

// FlowRow layout helper for world graph
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun FlowRow(
    modifier: Modifier = Modifier,
    horizontalArrangement: Arrangement.Horizontal = Arrangement.Start,
    verticalArrangement: Arrangement.Vertical = Arrangement.Top,
    content: @Composable () -> Unit
) {
    androidx.compose.foundation.layout.FlowRow(
        modifier = modifier,
        horizontalArrangement = horizontalArrangement,
        verticalArrangement = verticalArrangement
    ) {
        content()
    }
}

@Composable
fun ProgressIndicatorRow(
    label: String,
    value: Float,
    color: Color
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            color = TextPrincipal.copy(alpha = 0.65f),
            fontFamily = FontFamily.Monospace,
            fontSize = 10.sp,
            modifier = Modifier.width(130.dp)
        )
        Spacer(modifier = Modifier.width(6.dp))
        LinearProgressIndicator(
            progress = { value },
            color = color,
            trackColor = color.copy(alpha = 0.15f),
            modifier = Modifier
                .weight(1f)
                .height(4.dp)
                .clip(RoundedCornerShape(2.dp))
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = String.format("%.2f", value),
            color = color,
            fontFamily = FontFamily.Monospace,
            fontWeight = FontWeight.Bold,
            fontSize = 10.sp,
            modifier = Modifier.width(36.dp),
            textAlign = TextAlign.End
        )
    }
}

@Composable
fun ChatBubbleContainer(message: Message) {
    val isUser = message.sender == Sender.USER
    val format = remember { SimpleDateFormat("HH:mm:ss", Locale.getDefault()) }
    val timeString = remember(message.timestampMs) { format.format(Date(message.timestampMs)) }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .testTag("msg_${message.id}"),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(0.85f),
            horizontalAlignment = if (isUser) Alignment.End else Alignment.Start
        ) {
            // Message bubble content
            Box(
                modifier = Modifier
                    .clip(
                        if (isUser) {
                            RoundedCornerShape(
                                topStart = 16.dp,
                                topEnd = 16.dp,
                                bottomStart = 16.dp,
                                bottomEnd = 0.dp
                            )
                        } else {
                            RoundedCornerShape(
                                topStart = 16.dp,
                                topEnd = 16.dp,
                                bottomStart = 0.dp,
                                bottomEnd = 16.dp
                            )
                        }
                    )
                    .background(
                        if (isUser) {
                            CyanTint10
                        } else {
                            DarkCardBg
                        }
                    )
                    .border(
                        width = 1.dp,
                        color = if (isUser) AccentCyan.copy(alpha = 0.4f) else AccentCyan.copy(alpha = 0.15f),
                        shape = if (isUser) {
                            RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp, bottomStart = 16.dp, bottomEnd = 0.dp)
                        } else {
                            RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp, bottomStart = 0.dp, bottomEnd = 16.dp)
                        }
                    )
                    .padding(horizontal = 14.dp, vertical = 10.dp)
            ) {
                Text(
                    text = message.text,
                    color = if (isUser) BubbleUserText else BubbleAetherText,
                    style = MaterialTheme.typography.bodyLarge,
                    modifier = Modifier.testTag("msg_text_${message.id}")
                )
            }

            Spacer(modifier = Modifier.height(3.dp))

            // Footer with metadata
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(6.dp),
                modifier = Modifier.padding(horizontal = 4.dp)
            ) {
                if (!isUser) {
                    val isVerified = message.status == MessageStatus.VERIFIED
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(3.dp))
                            .background(
                                if (isVerified) StatusGreen.copy(alpha = 0.12f)
                                else StatusAmber.copy(alpha = 0.12f)
                            )
                            .padding(horizontal = 4.dp, vertical = 2.dp)
                    ) {
                        Text(
                            text = if (isVerified) "VERIFICADA" else "INCIERTO",
                            color = if (isVerified) StatusGreen else StatusAmber,
                            style = MaterialTheme.typography.labelSmall,
                            fontSize = 8.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                Text(
                    text = timeString,
                    color = TextPrincipal.copy(alpha = 0.45f),
                    fontFamily = FontFamily.Monospace,
                    fontSize = 9.sp
                )
            }
        }
    }
}
