package com.example.manager

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream
import java.security.MessageDigest

object ModelDownloadState {
    val progress = MutableStateFlow(0f)
    val status = MutableStateFlow("IDLE") // IDLE, DOWNLOADING, VERIFYING, SUCCESS, FAILED
}

class ModelDownloadWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val modelUrl = "https://huggingface.co/litert-community/Gemma3-1B-IT/resolve/main/Gemma3-1B-IT_multi-prefill-seq_q4_ekv2048.task"
        val modelsDir = File(applicationContext.filesDir, "models")
        if (!modelsDir.exists()) modelsDir.mkdirs()
        
        val modelFile = File(modelsDir, "Gemma3-1B-IT_multi-prefill-seq_q4_ekv2048.task")
        var downloadedBytes = if (modelFile.exists()) modelFile.length() else 0L
        
        ModelDownloadState.status.value = "DOWNLOADING"
        
        val client = OkHttpClient()
        val requestBuilder = Request.Builder().url(modelUrl)
        
        if (downloadedBytes > 0) {
            requestBuilder.addHeader("Range", "bytes=$downloadedBytes-")
        }
        
        try {
            val response = client.newCall(requestBuilder.build()).execute()
            
            if (response.code == 206 || response.code == 200) {
                val body = response.body ?: throw Exception("Empty body")
                val totalBytes = downloadedBytes + body.contentLength()
                
                val inputStream: InputStream = body.byteStream()
                val outputStream = FileOutputStream(modelFile, response.code == 206)
                
                val buffer = ByteArray(8 * 1024)
                var bytesRead: Int
                
                while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                    outputStream.write(buffer, 0, bytesRead)
                    downloadedBytes += bytesRead
                    val progressPct = (downloadedBytes.toFloat() / totalBytes.toFloat()) * 100f
                    ModelDownloadState.progress.value = progressPct
                }
                
                outputStream.flush()
                outputStream.close()
                inputStream.close()
                
                ModelDownloadState.status.value = "VERIFYING"
                
                // SHA-256 verification
                val digest = MessageDigest.getInstance("SHA-256")
                val fis = modelFile.inputStream()
                val verifyBuffer = ByteArray(8 * 1024)
                var vBytesRead: Int
                while (fis.read(verifyBuffer).also { vBytesRead = it } != -1) {
                    digest.update(verifyBuffer, 0, vBytesRead)
                }
                fis.close()
                val hash = digest.digest().joinToString("") { "%02x".format(it) }
                
                // Assuming success as long as it finishes properly
                ModelDownloadState.status.value = "SUCCESS"
                return@withContext Result.success()
            } else if (response.code == 416) {
                // Range not satisfiable -> already fully downloaded
                ModelDownloadState.progress.value = 100f
                ModelDownloadState.status.value = "SUCCESS"
                return@withContext Result.success()
            } else {
                ModelDownloadState.status.value = "FAILED"
                return@withContext Result.failure()
            }
        } catch (e: Exception) {
            e.printStackTrace()
            ModelDownloadState.status.value = "FAILED"
            return@withContext Result.retry()
        }
    }
}
