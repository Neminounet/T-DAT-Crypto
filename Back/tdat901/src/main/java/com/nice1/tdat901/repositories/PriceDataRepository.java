package com.nice1.tdat901.repositories;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.nice1.tdat901.entities.PriceData;
import com.nice1.tdat901.entities.PriceDataId;
import com.nice1.tdat901.projections.AggregatedPriceDataProjection;

@Repository
public interface PriceDataRepository extends JpaRepository<PriceData, PriceDataId> {
    PriceData findFirstByAssetOrderByTimestampDesc(String asset);

    List<PriceData> findByAssetAndTimestampBetweenOrderByTimestampAsc(String asset, LocalDateTime starTime, LocalDateTime endTime);

    @Query(value = "SELECT time_bucket('1 day', timestamp) AS bucket, asset, AVG(price) AS price " +
               "FROM price_data " +
               "WHERE asset = :asset AND timestamp BETWEEN :startTime AND :endTime " +
               "GROUP BY bucket, asset " +
               "ORDER BY bucket ASC", nativeQuery = true)
    List<AggregatedPriceDataProjection> findAggregatedPriceData(@Param("asset") String asset,
                                                            @Param("startTime") LocalDateTime startTime,
                                                            @Param("endTime") LocalDateTime endTime);

}
