package com.example.model

data class NodeItem(
    val name: String,
    val type: String = "concept",
    val weight: Float
)

data class BeliefItem(
    val concept: String,
    val value: String,
    val confidence: Float,
    val source: String
)

data class IntrospectionItem(
    val type: String,
    val content: String,
    val timestamp: String
)

data class VisionItem(
    val timestamp: String,
    val trigger: String,
    val camara: String,
    val description: String
)
