package com.example.core

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import android.util.Log

class UpdateWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        Log.i("UpdateWorker", "Checking for AETHER internal updates...")
        AetherCoreService.registrarError("UpdateWorker", "Buscando actualizaciones semanales programadas...")
        // Enviar aviso al sistema core
        return Result.success()
    }
}
