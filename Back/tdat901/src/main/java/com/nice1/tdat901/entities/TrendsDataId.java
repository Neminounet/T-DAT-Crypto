package com.nice1.tdat901.entities;

import java.io.Serializable;
import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;


@Data
@Embeddable
@NoArgsConstructor
@AllArgsConstructor
public class TrendsDataId implements Serializable {
    @Column(name = "timestamp")
    private LocalDateTime timestamp;

    @Column(name = "keyword")
    private String keyword;
}
