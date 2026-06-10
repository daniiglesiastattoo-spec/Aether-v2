package com.example.db

import androidx.room.TypeConverter
import com.example.model.MessageStatus
import com.example.model.Sender

class Converters {
    @TypeConverter
    fun fromSender(sender: Sender): String {
        return sender.name
    }

    @TypeConverter
    fun toSender(name: String): Sender {
        return Sender.valueOf(name)
    }

    @TypeConverter
    fun fromStatus(status: MessageStatus): String {
        return status.name
    }

    @TypeConverter
    fun toStatus(name: String): MessageStatus {
        return MessageStatus.valueOf(name)
    }
}
