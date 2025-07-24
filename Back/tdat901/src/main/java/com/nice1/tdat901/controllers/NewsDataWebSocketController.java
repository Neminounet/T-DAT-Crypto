package com.nice1.tdat901.controllers;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Controller;


import com.nice1.tdat901.entities.NewsData;
import com.nice1.tdat901.services.NewsDataService;

@Controller
public class NewsDataWebSocketController {

    @Autowired
    private SimpMessagingTemplate simpMessagingTemplate;

    @Autowired
    private NewsDataService newsDataService;
        
    @Scheduled(fixedRate = 300000) // 5 minutes :D 
    public void sendLatestNews() {
        List<NewsData> newNews = newsDataService.getLatestNews();
        if (newNews != null) {
            simpMessagingTemplate.convertAndSend("/topic/news/", newNews);
        }
    }
}
