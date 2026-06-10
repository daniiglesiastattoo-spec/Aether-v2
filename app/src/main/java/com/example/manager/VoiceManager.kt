package com.example.manager

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.util.Log
import java.util.Locale

/**
 * Interface and stub for Voice capability of AETHER, prepared for integration
 * with Android's SpeechRecognizer (STT) and TextToSpeech (TTS) engines.
 */
interface VoiceManager {
    fun startListening(onResult: (String) -> Unit, onError: (String) -> Unit)
    fun stopListening()
    fun speak(text: String, isOnlineMode: Boolean = false, onComplete: () -> Unit = {})
    fun shutdown()
}

/**
 * Concrete stub implementation of VoiceManager.
 */
class VoiceManagerImpl(private val context: Context) : VoiceManager {
    private val TAG = "AETHER_VoiceManager"
    
    private var textToSpeech: TextToSpeech? = null
    private var speechRecognizer: SpeechRecognizer? = null
    private var isTtsReady = false
    private val mainHandler = Handler(Looper.getMainLooper())

    init {
        textToSpeech = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                val langResult = textToSpeech?.setLanguage(Locale("es", "ES"))
                if (langResult == TextToSpeech.LANG_MISSING_DATA || langResult == TextToSpeech.LANG_NOT_SUPPORTED) {
                    textToSpeech?.setLanguage(Locale.getDefault())
                }
                isTtsReady = true
            }
        }
    }

    override fun startListening(onResult: (String) -> Unit, onError: (String) -> Unit) {
        mainHandler.post {
            if (!SpeechRecognizer.isRecognitionAvailable(context)) {
                onError("No disponible")
                return@post
            }

            if (speechRecognizer == null) {
                speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context)
            }

            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, "es-ES")
                putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
            }

            speechRecognizer?.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {}
                override fun onBeginningOfSpeech() {}
                override fun onRmsChanged(rmsdB: Float) {}
                override fun onBufferReceived(buffer: ByteArray?) {}
                override fun onEndOfSpeech() {}
                override fun onError(error: Int) {
                    val errorMsg = when(error) {
                        SpeechRecognizer.ERROR_AUDIO -> "Audio"
                        SpeechRecognizer.ERROR_CLIENT -> "Cliente"
                        SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Permiso Denegado"
                        SpeechRecognizer.ERROR_NETWORK -> "Red"
                        SpeechRecognizer.ERROR_NO_MATCH -> "No se entendió"
                        SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "Ocupado"
                        SpeechRecognizer.ERROR_SERVER -> "Servidor"
                        SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "Silencio corto"
                        else -> "Error ($error)"
                    }
                    Log.e(TAG, "STT Error: $errorMsg")
                    onError(errorMsg)
                }
                override fun onResults(results: Bundle?) {
                    val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    if (!matches.isNullOrEmpty()) {
                        onResult(matches[0])
                    } else {
                        onError("Vacío")
                    }
                }
                override fun onPartialResults(partialResults: Bundle?) {}
                override fun onEvent(eventType: Int, params: Bundle?) {}
            })

            speechRecognizer?.startListening(intent)
        }
    }

    override fun stopListening() {
        mainHandler.post {
            speechRecognizer?.stopListening()
        }
    }

    override fun speak(text: String, isOnlineMode: Boolean, onComplete: () -> Unit) {
        if (!isTtsReady || textToSpeech == null) {
            Log.w(TAG, "TTS not ready")
            onComplete()
            return
        }

        if (isOnlineMode) {
            textToSpeech?.setPitch(0.8f) 
            textToSpeech?.setSpeechRate(1.2f) 
        } else {
            textToSpeech?.setPitch(0.8f) 
            textToSpeech?.setSpeechRate(1.2f) 
        }

        val utteranceId = "Aether_TTS_${System.currentTimeMillis()}"
        textToSpeech?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {}
            override fun onDone(utteranceId: String?) { 
                mainHandler.post { onComplete() }
            }
            @Deprecated("Deprecated in Java", ReplaceWith("onComplete()"))
            override fun onError(utteranceId: String?) {
                mainHandler.post { onComplete() }
            }
        })
        textToSpeech?.speak(text, TextToSpeech.QUEUE_FLUSH, null, utteranceId)
    }

    override fun shutdown() {
        textToSpeech?.stop()
        textToSpeech?.shutdown()
        mainHandler.post {
            speechRecognizer?.destroy()
        }
    }
}
