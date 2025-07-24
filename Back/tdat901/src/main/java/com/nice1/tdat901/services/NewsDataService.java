package com.nice1.tdat901.services;

import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import com.nice1.tdat901.entities.NewsData;
import com.nice1.tdat901.repositories.NewsDataRepository;

@Service
public class NewsDataService {

    private NewsDataRepository newsDataRepository;
    
    public NewsDataService(NewsDataRepository newsDataRepository) {
        this.newsDataRepository = newsDataRepository;
    }
    
    public Page<NewsData> getNewsData(Pageable pageable) {
        return newsDataRepository.findAllByOrderByPublishedDesc(pageable);
    }
    
    public List<NewsData> getLatestNews() {
        return newsDataRepository.findTop10ByOrderByPublishedDesc();
    }
    
    public NewsData getNewsDataById(Integer id) {
        return newsDataRepository.findById(id).orElse(null);
    }
    
}
