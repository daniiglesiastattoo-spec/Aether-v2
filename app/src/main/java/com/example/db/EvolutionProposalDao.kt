package com.example.db

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.example.model.EvolutionProposal
import kotlinx.coroutines.flow.Flow

@Dao
interface EvolutionProposalDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertProposal(proposal: EvolutionProposal): Long

    @Query("SELECT * FROM evolution_proposals ORDER BY id DESC LIMIT :limit")
    suspend fun getRecentProposals(limit: Int): List<EvolutionProposal>

    @Query("SELECT * FROM evolution_proposals WHERE estado = 'pendiente' ORDER BY id ASC LIMIT :limit")
    suspend fun getPendingProposals(limit: Int): List<EvolutionProposal>

    @Query("UPDATE evolution_proposals SET estado = 'comunicada' WHERE estado = 'pendiente'")
    suspend fun markPendingAsCommunicated()

    @Query("UPDATE evolution_proposals SET estado = :newState WHERE id = :id")
    suspend fun updateProposalState(id: Int, newState: String)
}
