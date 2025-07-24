package com.nice1.tdat901.controllers;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.nice1.tdat901.dtos.AggregatedPriceDataDTO;
import com.nice1.tdat901.entities.PriceData;
import com.nice1.tdat901.services.PriceDataService;

@RestController
@RequestMapping("/api/prices")
public class PriceDataRestController {

    @Autowired
    private PriceDataService priceDataService;

    @GetMapping("/{asset}/history")
    public List<AggregatedPriceDataDTO> getPriceHistory(@PathVariable String asset, @RequestParam String period) {
        // period : 1d, 1w, 1m, 3m, 6m, 1y
        LocalDateTime endTime = LocalDateTime.now();
        LocalDateTime startTime = calculateStartTime(period, endTime);

        //return priceDataService.getPriceDataForAssetAndPeriod(asset, startTime, endTime);
        return priceDataService.getAggregatedPriceData(asset, startTime, endTime);
    }

    private LocalDateTime calculateStartTime(String period, LocalDateTime endTime) {
        switch (period) {
        case "1d":
            return endTime.minus(1, ChronoUnit.DAYS);
        case "1w":
            return endTime.minus(1, ChronoUnit.WEEKS);
        case "1m":
            return endTime.minus(1, ChronoUnit.MONTHS);
        case "3m":
            return endTime.minus(3, ChronoUnit.MONTHS);
        case "6m":
            return endTime.minus(6, ChronoUnit.MONTHS);
        case "1y":
            return endTime.minus(1, ChronoUnit.YEARS);
        default:
            throw new IllegalArgumentException("Période invalide: " + period);
        }
    }

    @GetMapping("/assets")
    public List<String> getAvailableAssets() {
        return priceDataService.getAvailableAssets();
    }

    @GetMapping("/latest")
    public List<PriceData> getLatestPrices() {
        return priceDataService.getLatestPricesForAllAssets();
    }
}
