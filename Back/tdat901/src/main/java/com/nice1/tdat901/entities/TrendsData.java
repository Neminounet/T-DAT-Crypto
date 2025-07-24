package com.nice1.tdat901.entities;

import jakarta.persistence.Column;
import jakarta.persistence.EmbeddedId;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "trends_data")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TrendsData {

    @EmbeddedId
    private TrendsDataId id;

    @Column(name = "interest")
    private Integer interest;

    @Column(name = "is_partial")
    private Boolean isPartial;

}
