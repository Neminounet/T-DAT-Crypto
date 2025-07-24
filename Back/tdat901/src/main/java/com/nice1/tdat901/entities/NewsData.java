package com.nice1.tdat901.entities;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "news_data")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class NewsData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;

    @Column(name = "title", nullable = false)
    private String title;

    @Column(name = "link", nullable = false)
    private String link;

    @Column(name = "published", nullable = false)
    private LocalDateTime published;

    @Column(name = "summary")
    private String summary;

    @Column(name = "source")
    private String source;

    @Column(name = "image_url")
    private String imageUrl;

    @Column(name = "sentiment")
    private Double sentiment;

}