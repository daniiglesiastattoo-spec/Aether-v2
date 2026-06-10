package com.example.db

import com.example.model.Message
import kotlinx.coroutines.flow.Flow

class MessageRepository(private val messageDao: MessageDao) {
    val allMessages: Flow<List<Message>> = messageDao.getAllMessages()

    suspend fun insert(message: Message) {
        messageDao.insertMessage(message)
    }

    suspend fun clearAll() {
        messageDao.clearMessages()
    }
}
