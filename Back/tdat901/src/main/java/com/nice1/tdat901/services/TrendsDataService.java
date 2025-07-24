package com.nice1.tdat901.services;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.stereotype.Service;

import com.nice1.tdat901.entities.TrendsData;
import com.nice1.tdat901.repositories.TrendsDataRepository;

@Service
public class TrendsDataService {

    private TrendsDataRepository trendsDataRepository;

    public TrendsDataService(TrendsDataRepository trendsDataRepository) {
        this.trendsDataRepository = trendsDataRepository;
    }

    public List<TrendsData> getLatestTrendsData() {
        return trendsDataRepository.findById_TimestampOrderById_KeywordDesc(getLatestTimestamp());
    }

    private LocalDateTime getLatestTimestamp() {
        return trendsDataRepository.findMaxTimestamp();
    }
}
