package com.nice1.tdat901.repositories;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.nice1.tdat901.entities.TrendsData;
import com.nice1.tdat901.entities.TrendsDataId;

@Repository
public interface TrendsDataRepository extends JpaRepository<TrendsData, TrendsDataId> {

    @Query("SELECT MAX(t.id.timestamp) FROM TrendsData t")
    LocalDateTime findMaxTimestamp();

    List<TrendsData> findById_TimestampOrderById_KeywordDesc(LocalDateTime timestamp);

}
