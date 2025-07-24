package com.nice1.tdat901.entities;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "price_data")
@IdClass(PriceDataId.class)
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PriceData {

    @Id
    @Column(name = "timestamp")
    private LocalDateTime timestamp;

    @Id
    @Column(name = "asset")
    private String asset;

    @Column(name = "price")
    private BigDecimal price;
}
