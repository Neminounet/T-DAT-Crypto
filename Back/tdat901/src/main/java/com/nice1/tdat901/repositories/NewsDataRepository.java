package com.nice1.tdat901.repositories;

import java.time.LocalDateTime;

import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import com.nice1.tdat901.entities.NewsData;

public interface NewsDataRepository  extends JpaRepository<NewsData, Integer> {

    Page<NewsData> findAllByOrderByPublishedDesc(Pageable pageable);

    List<NewsData> findTop10ByOrderByPublishedDesc();

    List<NewsData> findByPublishedAfterOrderByPublishedDesc(LocalDateTime published);

}
