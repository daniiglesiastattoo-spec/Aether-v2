package com.example.manager

import android.content.Context
import android.util.Log
import com.google.mediapipe.tasks.genai.llminference.LlmInference
import kotlinx.coroutines.flow.MutableStateFlow
import java.io.File

object LocalLlmEngine {
    enum class State {
        NOT_DOWNLOADED, DOWNLOADING, READY, LOADED, FAILED
    }

    val state = MutableStateFlow(State.NOT_DOWNLOADED)
    private var llmInference: LlmInference? = null
    
    fun checkModelState(context: Context) {
        val modelFile = File(context.filesDir, "models/Gemma3-1B-IT_multi-prefill-seq_q4_ekv2048.task")
        if (modelFile.exists()) {
            state.value = State.READY
        } else {
            state.value = State.NOT_DOWNLOADED
        }
    }

    fun load(context: Context): Boolean {
        if (state.value == State.LOADED) return true
        val modelFile = File(context.filesDir, "models/Gemma3-1B-IT_multi-prefill-seq_q4_ekv2048.task")
        if (!modelFile.exists()) {
            state.value = State.NOT_DOWNLOADED
            return false
        }
        
        return try {
            val options = LlmInference.LlmInferenceOptions.builder()
                .setModelPath(modelFile.absolutePath)
                .setMaxTokens(512)
                
                
                .build()
                
            llmInference = LlmInference.createFromOptions(context, options)
            state.value = State.LOADED
            true
        } catch (e: OutOfMemoryError) {
            Log.e("LocalLlmEngine", "OOM loading local model", e)
            state.value = State.FAILED
            false
        } catch (e: Exception) {
            Log.e("LocalLlmEngine", "Error loading local model", e)
            state.value = State.FAILED
            false
        }
    }
    
    fun unload() {
        try {
            llmInference?.close()
        } catch (e: Exception) {
            Log.e("LocalLlmEngine", "Error closing engine", e)
        }
        llmInference = null
        if (state.value == State.LOADED || state.value == State.FAILED) {
            state.value = State.READY
        }
    }
    
    fun generateResponse(prompt: String): Result<String> {
        val engine = llmInference ?: return Result.failure(Exception("Engine not loaded"))
        return try {
            val result = engine.generateResponse(prompt)
            Result.success(result)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
