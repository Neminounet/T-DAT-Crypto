package com.nice1.tdat901.entities;

import java.io.Serializable;
import java.time.LocalDateTime;

import jakarta.persistence.Embeddable;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Embeddable
@NoArgsConstructor
@AllArgsConstructor
public class PriceDataId implements Serializable {
    private LocalDateTime timestamp;
    private String asset;
}
