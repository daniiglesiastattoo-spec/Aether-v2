package com.example.db

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.example.model.Reflexion
import kotlinx.coroutines.flow.Flow

@Dao
interface ReflexionDao {
    @Query("SELECT * FROM reflexiones WHERE activa = 1 ORDER BY id DESC")
    suspend fun getActiveReflexiones(): List<Reflexion>

    @Query("SELECT MAX(ultimoMsgTimestamp) FROM reflexiones")
    suspend fun getLastReflexionTimestamp(): Long?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertReflexion(reflexion: Reflexion)
}
