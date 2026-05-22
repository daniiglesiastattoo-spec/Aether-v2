package com.example.manager

import android.content.Context
import android.util.Log

/**
 * Interface and stub for Voice capability of AETHER, prepared for integration
 * with Android's SpeechRecognizer (STT) and TextToSpeech (TTS) engines.
 */
interface VoiceManager {
    fun startListening(onResult: (String) -> Unit, onError: (String) -> Unit)
    fun stopListening()
    fun speak(text: String, onComplete: () -> Unit = {})
    fun shutdown()
}

/**
 * Concrete stub implementation of VoiceManager.
 */
class VoiceManagerImpl(private val context: Context) : VoiceManager {
    private val TAG = "AETHER_VoiceManager"

    override fun startListening(onResult: (String) -> Unit, onError: (String) -> Unit) {
        Log.d(TAG, "SpeechRecognizer: startListening stub activated.")
        // Prepared to instantiate android.speech.SpeechRecognizer
    }

    override fun stopListening() {
        Log.d(TAG, "SpeechRecognizer: stopListening stub activated.")
    }

    override fun speak(text: String, onComplete: () -> Unit) {
        Log.d(TAG, "TextToSpeech: speak text: \"$text\"")
        // Prepared to instantiate android.speech.tts.TextToSpeech
        onComplete()
    }

    override fun shutdown() {
        Log.d(TAG, "VoiceManager: shutdown resource release.")
    }
}
