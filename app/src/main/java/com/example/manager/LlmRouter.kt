package com.example.manager

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import com.example.net.ApiPriority
import com.example.net.ApiProvider
import com.example.net.CircuitBreaker
import kotlinx.coroutines.flow.MutableStateFlow

enum class LlmMode {
    AUTO, LOCAL_ONLY, CLOUD_ONLY
}

object LlmRouter {
    val currentMode = MutableStateFlow(LlmMode.AUTO)
    val activeEngine = MutableStateFlow("UNKNOWN")
    
    fun setMode(mode: LlmMode) {
        currentMode.value = mode
    }

    private fun getBatteryPercentage(context: Context): Int {
        val batteryStatus: Intent? = IntentFilter(Intent.ACTION_BATTERY_CHANGED).let { ifilter ->
            context.registerReceiver(null, ifilter)
        }
        val level: Int = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale: Int = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        return if (level != -1 && scale != -1) {
            (level * 100 / scale.toFloat()).toInt()
        } else {
            100
        }
    }

    suspend fun routeAndGenerate(
        context: Context,
        prompt: String,
        systemInstruction: String,
        priority: ApiPriority,
        apiKey: String
    ): Result<String> {
        val mode = currentMode.value
        val batteryPct = getBatteryPercentage(context)
        
        val canUseCloud = mode == LlmMode.AUTO || mode == LlmMode.CLOUD_ONLY
        val canUseLocal = mode == LlmMode.AUTO || mode == LlmMode.LOCAL_ONLY
        
        val shouldTryCloudFirst = canUseCloud && batteryPct >= 15 && CircuitBreaker.isAvailable(ApiProvider.GEMINI)
        
        if (shouldTryCloudFirst || mode == LlmMode.CLOUD_ONLY) {
            activeEngine.value = "CLOUD (Gemini)"
            val request = GenerateContentRequest(
                systemInstruction = Content(parts = listOf(Part(text = systemInstruction))),
                contents = listOf(Content(role = "user", parts = listOf(Part(text = prompt))))
            )
            val result = GeminiClient.generateContentSafe(apiKey, request, priority)
            if (result.isSuccess) {
                return result
            }
            if (mode == LlmMode.CLOUD_ONLY) {
                return result
            }
        }
        
        if (canUseLocal) {
            activeEngine.value = "LOCAL (Gemma 3)"
            if (LocalLlmEngine.state.value != LocalLlmEngine.State.LOADED) {
                val loaded = LocalLlmEngine.load(context)
                if (!loaded) return Result.failure(Exception("Modelo local no descargado o fallo de memoria (OOM)"))
            }
            val fullPrompt = "$systemInstruction\n\nUser: $prompt\nModel:"
            return LocalLlmEngine.generateResponse(fullPrompt)
        }
        
        return Result.failure(Exception("Sin ruta viable"))
    }
}
