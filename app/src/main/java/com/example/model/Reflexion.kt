package com.example.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(tableName = "reflexiones")
data class Reflexion(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val ts: String,
    val ultimoMsgTimestamp: Long, // Maps to ultimo_msg_id in python
    val resumen: String,
    val impactoUsuario: String,
    val impactoPropio: String,
    val comparacion: String,
    val conclusion: String,
    val tags: String,
    val usos: Int = 0,
    val activa: Boolean = true
)
