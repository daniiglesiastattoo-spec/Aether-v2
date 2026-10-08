package com.example.net

import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class TokenBucket(
    val maxTokens: Int,
    val refillRatePerMinute: Int
) {
    var tokens: Float = maxTokens.toFloat()
    var lastRefillTime: Long = System.currentTimeMillis()
    
    fun refill() {
        val now = System.currentTimeMillis()
        val elapsedMinutes = (now - lastRefillTime) / 60000f
        val addedTokens = elapsedMinutes * refillRatePerMinute
        if (addedTokens > 0) {
            tokens = minOf(maxTokens.toFloat(), tokens + addedTokens)
            lastRefillTime = now
        }
    }
}

object RateLimiter {
    private val mutex = Mutex()
    
    // Configurable buckets. Free tiers usually have limits like 15 RPM for Gemini.
    private val buckets = mutableMapOf(
        ApiProvider.GEMINI to TokenBucket(maxTokens = 15, refillRatePerMinute = 15),
        ApiProvider.GROQ to TokenBucket(maxTokens = 30, refillRatePerMinute = 30)
    )
    
    suspend fun acquire(provider: ApiProvider, priority: ApiPriority): Boolean = mutex.withLock {
        val bucket = buckets[provider] ?: return@withLock false
        bucket.refill()
        
        if (priority == ApiPriority.BACKGROUND_REFLEXION) {
            val percentage = bucket.tokens / bucket.maxTokens
            if (percentage < 0.3f) {
                return@withLock false
            }
        }
        
        if (bucket.tokens >= 1f) {
            bucket.tokens -= 1f
            return@withLock true
        }
        return@withLock false
    }
}
