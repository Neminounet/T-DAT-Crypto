package com.nice1.tdat901.controllers;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.nice1.tdat901.entities.TrendsData;
import com.nice1.tdat901.services.TrendsDataService;

@RestController
@RequestMapping("/api/trends")
public class TrendsDataRestController {

    @Autowired
    private TrendsDataService trendsDataService;

    @GetMapping("/latest") 
    public ResponseEntity<List<TrendsData>> getLatestTrendsData() {
        List<TrendsData> trendsData = trendsDataService.getLatestTrendsData();
        if (trendsData.isEmpty() || trendsData == null) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.ok(trendsData);
    }
}
