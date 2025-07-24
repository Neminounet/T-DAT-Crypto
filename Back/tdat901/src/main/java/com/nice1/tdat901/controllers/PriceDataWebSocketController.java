package com.nice1.tdat901.controllers;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Controller;

import com.nice1.tdat901.entities.PriceData;
import com.nice1.tdat901.services.PriceDataService;

@Controller
public class PriceDataWebSocketController {

    @Autowired
    private SimpMessagingTemplate simpMessagingTemplate;

    @Autowired
    private PriceDataService priceDataService;

    private String[] assets = new String[] { "BTCEUR", "ETHEUR", "BNBEUR", "SOLEUR", "XRPEUR", "ADAEUR", "DOGEEUR", "LTCEUR", "XLMEUR", "TRXEUR" };

    @Scheduled(fixedRate = 5000)
    public void sendLatestPrice() {
        for (String asset : assets) {
            PriceData latestPrice = priceDataService.getLatestPriceForAsset(asset);
            if (latestPrice != null) {
                simpMessagingTemplate.convertAndSend("/topic/price/" + asset, latestPrice);
            }
        }
        
        List<PriceData> latestPrices = priceDataService.getLatestPricesForAllAssets();
        if (latestPrices != null) {
            simpMessagingTemplate.convertAndSend("/topic/price/", latestPrices);
        }
    }
}
