import re

with open('app/src/main/java/com/example/core/AetherCoreService.kt', 'r') as f:
    content = f.read()

bad_def = """    private fun iniciarLatido()
        // Programar actualizacion automatica semanal
        val updateRequest = PeriodicWorkRequestBuilder<UpdateWorker>(7, TimeUnit.DAYS)
            .build()
        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "WeeklyUpdate",
            ExistingPeriodicWorkPolicy.KEEP,
            updateRequest
        ) {"""

good_def = """    private fun iniciarLatido() {"""

content = content.replace(bad_def, good_def)

with open('app/src/main/java/com/example/core/AetherCoreService.kt', 'w') as f:
    f.write(content)
