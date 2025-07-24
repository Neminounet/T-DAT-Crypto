package com.nice1.tdat901.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.nice1.tdat901.entities.NewsData;
import com.nice1.tdat901.services.NewsDataService;

@RestController
@RequestMapping("/api/news")
public class NewsDataRestController {

    @Autowired
    private NewsDataService newsDataService;

    @GetMapping("")
    public ResponseEntity<Page<NewsData>> getLatestNewsData(
        @RequestParam(defaultValue = "0") Integer page,
        @RequestParam(defaultValue = "10") Integer size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<NewsData> newsDataPage = newsDataService.getNewsData(pageable);
        return ResponseEntity.ok(newsDataPage);
    }

    @GetMapping("/{id}")
    public ResponseEntity<NewsData> getNewsDataById(@PathVariable Integer id) {
        NewsData newsData = newsDataService.getNewsDataById(id);
        if (newsData == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(newsData);
    }
}
