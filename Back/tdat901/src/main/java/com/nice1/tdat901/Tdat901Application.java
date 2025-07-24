package com.nice1.tdat901;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class Tdat901Application {

	public static void main(String[] args) {
		SpringApplication.run(Tdat901Application.class, args);
	}

}
