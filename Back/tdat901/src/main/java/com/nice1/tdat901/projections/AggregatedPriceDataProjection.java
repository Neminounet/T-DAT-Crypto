package com.nice1.tdat901.projections;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public interface AggregatedPriceDataProjection {
    LocalDateTime getBucket();
    String getAsset();
    BigDecimal getPrice();
}
