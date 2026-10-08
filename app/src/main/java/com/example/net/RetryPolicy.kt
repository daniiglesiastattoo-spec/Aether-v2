package com.example.net

import kotlinx.coroutines.delay
import retrofit2.HttpException
import kotlin.random.Random

object RetryPolicy {
    suspend fun <T> executeWithRetry(
        provider: ApiProvider,
        priority: ApiPriority,
        block: suspend () -> T
    ): Result<T> {
        var attempt = 0
        val maxAttempts = 4
        
        while (attempt < maxAttempts) {
            // Wait for rate limiter
            while (!RateLimiter.acquire(provider, priority)) {
                if (priority == ApiPriority.BACKGROUND_REFLEXION) {
                    return Result.failure(Exception("Rate limit exceeded for BACKGROUND_REFLEXION"))
                }
                delay(1000) // Wait 1 sec if user chat is throttled by bucket
            }
            
            // Check circuit breaker
            if (!CircuitBreaker.isAvailable(provider)) {
                return Result.failure(Exception("Circuit breaker is OPEN for provider $provider"))
            }
            
            try {
                val result = block()
                CircuitBreaker.recordSuccess(provider)
                return Result.success(result)
            } catch (e: Exception) {
                val is429 = (e as? HttpException)?.code() == 429 || e.message?.contains("429") == true
                
                if (is429) {
                    CircuitBreaker.recordFailure429(provider)
                    
                    if (!CircuitBreaker.isAvailable(provider)) {
                        return Result.failure(Exception("Circuit breaker tripped for provider $provider due to repeated 429s"))
                    }
                    
                    attempt++
                    if (attempt >= maxAttempts) {
                        return Result.failure(e)
                    }
                    
                    val retrofitHttpException = e as? HttpException
                    val retryAfterStr = retrofitHttpException?.response()?.headers()?.get("Retry-After")
                    val retryAfterSecs = retryAfterStr?.toLongOrNull()
                    
                    val waitMs = if (retryAfterSecs != null && retryAfterSecs > 0) {
                        retryAfterSecs * 1000L
                    } else {
                        val baseDelay = (1 shl (attempt - 1)) * 1000L // 1s, 2s, 4s, 8s
                        val jitter = Random.nextLong(0, 500)
                        baseDelay + jitter
                    }
                    delay(waitMs)
                } else {
                    return Result.failure(e)
                }
            }
        }
        return Result.failure(Exception("Max retry attempts reached"))
    }
}
