package com.nice1.tdat901.dtos;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class AggregatedPriceDataDTO {
    private LocalDateTime bucket;
    private String asset;
    private BigDecimal price;
}
