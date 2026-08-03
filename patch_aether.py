import re

with open('app/src/main/java/com/example/core/AetherCoreService.kt', 'r') as f:
    content = f.read()

import_statement = "import androidx.work.PeriodicWorkRequestBuilder\nimport androidx.work.WorkManager\nimport java.util.concurrent.TimeUnit\nimport androidx.work.ExistingPeriodicWorkPolicy"

if "androidx.work.WorkManager" not in content:
    content = re.sub(r'import android\.util\.Log', import_statement + '\nimport android.util.Log', content)

schedule_code = """
        // Programar actualizacion automatica semanal
        val updateRequest = PeriodicWorkRequestBuilder<UpdateWorker>(7, TimeUnit.DAYS)
            .build()
        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "WeeklyUpdate",
            ExistingPeriodicWorkPolicy.KEEP,
            updateRequest
        )
"""

if "WeeklyUpdate" not in content:
    content = re.sub(r'iniciarLatido\(\)', r'iniciarLatido()' + schedule_code, content)

with open('app/src/main/java/com/example/core/AetherCoreService.kt', 'w') as f:
    f.write(content)
