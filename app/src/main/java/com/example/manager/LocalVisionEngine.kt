package com.example.manager

import android.content.Context
import android.graphics.Bitmap
import android.util.Log
import com.google.mediapipe.framework.image.BitmapImageBuilder
import com.google.mediapipe.tasks.core.BaseOptions
import com.google.mediapipe.tasks.vision.imageclassifier.ImageClassifier
import com.google.mediapipe.tasks.vision.objectdetector.ObjectDetector
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class LocalVisionEngine(private val context: Context) {
    private val TAG = "AETHER_LocalVision"
    private var objectDetector: ObjectDetector? = null
    private var imageClassifier: ImageClassifier? = null

    init {
        try {
            val baseOptionsDet = BaseOptions.builder()
                .setModelAssetPath("efficientdet_lite0.tflite")
                .build()
            val optionsDet = ObjectDetector.ObjectDetectorOptions.builder()
                .setBaseOptions(baseOptionsDet)
                .setMaxResults(5)
                .setScoreThreshold(0.4f)
                .build()
            objectDetector = ObjectDetector.createFromOptions(context, optionsDet)

            val baseOptionsCls = BaseOptions.builder()
                .setModelAssetPath("efficientnet_lite0.tflite")
                .build()
            val optionsCls = ImageClassifier.ImageClassifierOptions.builder()
                .setBaseOptions(baseOptionsCls)
                .setMaxResults(3)
                .setScoreThreshold(0.3f)
                .build()
            imageClassifier = ImageClassifier.createFromOptions(context, optionsCls)
        } catch (e: Exception) {
            Log.e(TAG, "Error initializing MediaPipe: ${e.message}")
        }
    }

    suspend fun analyze(bitmap: Bitmap): String = withContext(Dispatchers.Default) {
        try {
            val mpImage = BitmapImageBuilder(bitmap).build()
            
            val detections = objectDetector?.detect(mpImage)
            val classifications = imageClassifier?.classify(mpImage)

            val detectedObjects = detections?.detections()?.flatMap { it.categories() }
                ?.map { it.categoryName() }
                ?.distinct()
                ?: emptyList()

            val classifiedCategories = classifications?.classificationResult()?.classifications()?.firstOrNull()?.categories()
                ?.map { it.categoryName() }
                ?: emptyList()

            val combined = (detectedObjects + classifiedCategories).distinct()

            if (combined.isEmpty()) {
                "No detecto objetos reconocibles con certeza."
            } else {
                combined.joinToString(", ")
            }
        } catch (e: Exception) {
            "Error de análisis local."
        }
    }
}
