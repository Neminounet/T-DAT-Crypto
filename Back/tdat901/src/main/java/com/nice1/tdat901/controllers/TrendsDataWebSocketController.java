package com.nice1.tdat901.controllers;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.event.EventListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Controller;
import org.springframework.web.socket.messaging.SessionSubscribeEvent;

import com.nice1.tdat901.entities.TrendsData;
import com.nice1.tdat901.services.TrendsDataService;

@Controller
public class TrendsDataWebSocketController {

    @Autowired
    private SimpMessagingTemplate simpMessagingTemplate;

    @Autowired
    private TrendsDataService trendsDataService;

    @Scheduled(cron = "0 0 0/1 * * *") // Toutes les heures à normalement 0 min
    public void sendLatestTrends() {
        List<TrendsData> newTrends = trendsDataService.getLatestTrendsData();
        if (newTrends != null && !newTrends.isEmpty()) {
            simpMessagingTemplate.convertAndSend("/topic/trends/", newTrends);
        }
    }

    @EventListener
    public void handleSessionSubscribe(SessionSubscribeEvent event) {
        String destination = Optional.ofNullable(event.getMessage().getHeaders().get("simpDestination"))
                                     .map(Object::toString)
                                     .orElse("");
        if (destination.equals("/topic/trends/")) {
            List<TrendsData> newTrends = trendsDataService.getLatestTrendsData();
            if (newTrends != null && !newTrends.isEmpty()) {
                simpMessagingTemplate.convertAndSend("/topic/trends/", newTrends);
            }
        }
    }
}
