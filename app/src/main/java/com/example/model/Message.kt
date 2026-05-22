package com.example.model

import java.util.UUID

enum class Sender {
    USER,
    AETHER
}

enum class MessageStatus {
    VERIFIED,  // Displays "VERIFICADA" in green
    UNCERTAIN  // Displays "INCIERTO" in yellow/amber
}

data class Message(
    val id: String = UUID.randomUUID().toString(),
    val text: String,
    val sender: Sender,
    val timestampMs: Long = System.currentTimeMillis(),
    val status: MessageStatus = MessageStatus.VERIFIED
)
