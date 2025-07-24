package com.nice1.tdat901.services;

import java.time.LocalDateTime;
import java.util.List;

import java.util.ArrayList;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.nice1.tdat901.dtos.AggregatedPriceDataDTO;
import com.nice1.tdat901.entities.PriceData;
import com.nice1.tdat901.projections.AggregatedPriceDataProjection;
import com.nice1.tdat901.repositories.PriceDataRepository;

@Service
public class PriceDataService {

    @Autowired
    private PriceDataRepository priceDataRepository;

    private String[] assets = { "BTCEUR", "ETHEUR", "BNBEUR", "SOLEUR", "XRPEUR", "ADAEUR", "DOGEEUR", "LTCEUR", "XLMEUR", "TRXEUR" };

    public PriceData getLatestPriceForAsset(String asset) {
        return priceDataRepository.findFirstByAssetOrderByTimestampDesc(asset);
    }

    public List<PriceData> getPriceDataForAssetAndPeriod(String asset, LocalDateTime starTime, LocalDateTime endTime) {
        return priceDataRepository.findByAssetAndTimestampBetweenOrderByTimestampAsc(asset, starTime, endTime);
    }


    public List<String> getAvailableAssets() {
        return priceDataRepository.findAll().stream().map(PriceData::getAsset).distinct().toList();
    }

    public List<PriceData> getLatestPricesForAllAssets() {
        List<PriceData> latestPrices = new ArrayList<>();
        for (String asset : assets) {
            PriceData latestPrice = getLatestPriceForAsset(asset);
            if (latestPrice != null) {
                latestPrices.add(latestPrice);
            }
        }
        return latestPrices;
    }

    public List<AggregatedPriceDataDTO> getAggregatedPriceData(String asset, LocalDateTime startTime, LocalDateTime endTime) {
        List<AggregatedPriceDataProjection> projections = priceDataRepository.findAggregatedPriceData(asset, startTime, endTime);

        // Convertir les projections en DTO
        List<AggregatedPriceDataDTO> aggregatedData = new ArrayList<>();
        for (AggregatedPriceDataProjection projection : projections) {
            AggregatedPriceDataDTO dto = new AggregatedPriceDataDTO();
            dto.setBucket(projection.getBucket());
            dto.setAsset(projection.getAsset());
            dto.setPrice(projection.getPrice());
            aggregatedData.add(dto);
        }
        return aggregatedData;
    }
}
