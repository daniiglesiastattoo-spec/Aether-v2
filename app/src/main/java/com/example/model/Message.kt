package com.example.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.UUID

enum class Sender {
    USER,
    AETHER
}

enum class MessageStatus {
    VERIFIED,  // Displays "VERIFICADA" in green
    UNCERTAIN  // Displays "INCIERTO" in yellow/amber
}

@Entity(tableName = "messages")
data class Message(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val text: String,
    val sender: Sender,
    val timestampMs: Long = System.currentTimeMillis(),
    val status: MessageStatus = MessageStatus.VERIFIED
)
