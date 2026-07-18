package com.example.manager

import android.app.ActivityManager
import android.content.Context
import android.util.Log
import com.google.mediapipe.tasks.core.Delegate
import com.google.mediapipe.tasks.genai.llminference.LlmInference
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File

object LocalLlmEngine {

    private const val TAG = "LocalLlmEngine"
    private var llmInference: LlmInference? = null
    private const val MODEL_PATH_RELATIVE = "models/gemma3-1b-it.task"

    fun getModelFile(context: Context): File {
        return File(context.filesDir, MODEL_PATH_RELATIVE)
    }

    fun isModelAvailable(context: Context): Boolean {
        val file = getModelFile(context)
        return file.exists() && file.length() > 100 * 1024 * 1024
    }

    private var currentOnPartial: ((String) -> Unit)? = null
    private var currentOnDone: (() -> Unit)? = null

    private fun getMemoryInfo(context: Context): String {
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val memoryInfo = ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memoryInfo)
        val availMb = memoryInfo.availMem / (1024 * 1024)
        val totalMb = memoryInfo.totalMem / (1024 * 1024)
        return "RAM: ${availMb}MB de ${totalMb}MB"
    }

    suspend fun initializeIfNeeded(context: Context) {
        if (llmInference != null) return

        val modelFile = getModelFile(context)
        if (!modelFile.exists()) {
            throw IllegalStateException("Model file not found at ${modelFile.absolutePath}")
        }

        withContext(Dispatchers.IO) {
            val memInfo = getMemoryInfo(context)
            Log.i(TAG, "Initializing LLM. $memInfo")
            try {
                // Initialize with GPU first
                val optionsBuilderGPU = LlmInference.LlmInferenceOptions.builder()
                    .setModelPath(modelFile.absolutePath)
                    .setMaxTokens(512)
                    .setTopK(40)
                    .setTemperature(0.8f)
                    .setResultListener { partialResult, done ->
                        if (partialResult != null) {
                            currentOnPartial?.invoke(partialResult)
                        }
                        if (done) {
                            currentOnDone?.invoke()
                        }
                    }
                
                try {
                    val delegateMethod = optionsBuilderGPU.javaClass.getMethod("setDelegate", Delegate::class.java)
                    delegateMethod.invoke(optionsBuilderGPU, Delegate.GPU)
                } catch (e: Throwable) {
                    Log.w(TAG, "setDelegate(GPU) not found or failed, ignoring.")
                }
                
                try {
                    llmInference = LlmInference.createFromOptions(context, optionsBuilderGPU.build())
                    Log.i(TAG, "Local LLM Initialized successfully with GPU")
                } catch (eGPU: Throwable) {
                    Log.w(TAG, "Failed GPU initialization. Trying CPU. $memInfo", eGPU)
                    
                    val optionsBuilderCPU = LlmInference.LlmInferenceOptions.builder()
                        .setModelPath(modelFile.absolutePath)
                        .setMaxTokens(512)
                        .setTopK(40)
                        .setTemperature(0.8f)
                        .setResultListener { partialResult, done ->
                            if (partialResult != null) {
                                currentOnPartial?.invoke(partialResult)
                            }
                            if (done) {
                                currentOnDone?.invoke()
                            }
                        }
                        
                    try {
                        val delegateMethod = optionsBuilderCPU.javaClass.getMethod("setDelegate", Delegate::class.java)
                        delegateMethod.invoke(optionsBuilderCPU, Delegate.CPU)
                    } catch (e: Throwable) {
                        Log.w(TAG, "setDelegate(CPU) not found or failed, ignoring.")
                    }
                    
                    try {
                        llmInference = LlmInference.createFromOptions(context, optionsBuilderCPU.build())
                        Log.i(TAG, "Local LLM Initialized successfully with CPU")
                    } catch (eCPU: Throwable) {
                        throw Exception("GPU fail: ${eGPU.message} | CPU fail: ${eCPU.message}")
                    }
                }
            } catch (e: Throwable) {
                Log.e(TAG, "Failed to initialize Local LLM", e)
                throw Exception("Init Error (Memoria: ${getMemoryInfo(context)}): ${e.message}", e)
            }
        }
    }

    suspend fun generateStreaming(
        context: Context,
        prompt: String,
        onPartial: (String) -> Unit,
        onDone: () -> Unit
    ) {
        withContext(Dispatchers.IO) {
            try {
                initializeIfNeeded(context)
                currentOnPartial = onPartial
                currentOnDone = onDone

                val engine = llmInference ?: throw IllegalStateException("LLM Engine not initialized")
                
                engine.generateResponseAsync(prompt)
            } catch (e: Throwable) {
                Log.e(TAG, "Error generating response", e)
                throw Exception(e.message, e)
            }
        }
    }

    fun release() {
        try {
            llmInference?.close()
        } catch (e: Throwable) {
            Log.e(TAG, "Error releasing llmInference", e)
        }
        llmInference = null
        Log.i(TAG, "Local LLM released")
    }
}
