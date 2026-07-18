package com.example.model

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "evolution_proposals")
data class EvolutionProposal(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val hash: String,
    val timestamp: String,
    val categoria: String,
    val titulo: String,
    val problema: String,
    val propuesta: String,
    val evidencia: String,
    val riesgo: String,
    val estado: String = "pendiente" // pendiente, comunicada, aceptada, rechazada
)
