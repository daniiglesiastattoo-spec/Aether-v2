package com.example.net

import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

object CircuitBreaker {
    private val mutex = Mutex()
    
    private val consecutiveFailures = mutableMapOf<ApiProvider, Int>()
    private val openUntil = mutableMapOf<ApiProvider, Long>()
    
    suspend fun recordSuccess(provider: ApiProvider) = mutex.withLock {
        consecutiveFailures[provider] = 0
        openUntil.remove(provider)
    }
    
    suspend fun recordFailure429(provider: ApiProvider) = mutex.withLock {
        val count = (consecutiveFailures[provider] ?: 0) + 1
        consecutiveFailures[provider] = count
        
        if (count >= 3) {
            // Open circuit for 5 minutes (300_000 ms)
            openUntil[provider] = System.currentTimeMillis() + 5 * 60 * 1000L
        }
    }
    
    suspend fun isAvailable(provider: ApiProvider): Boolean = mutex.withLock {
        val until = openUntil[provider] ?: return@withLock true
        if (System.currentTimeMillis() >= until) {
            openUntil.remove(provider)
            consecutiveFailures[provider] = 0
            return@withLock true
        }
        return@withLock false
    }
}
