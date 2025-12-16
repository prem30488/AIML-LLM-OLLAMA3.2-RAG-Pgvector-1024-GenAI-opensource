package com.example.demo.sentiment.entity;

import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDateTime;

@Entity
@Table(name = "sentiment_feedback")
@Data
public class Feedback {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String content;

    private Double sentimentScore;

    private LocalDateTime createdAt = LocalDateTime.now();

    @Enumerated(EnumType.STRING)
    private SentimentType sentiment;

    public enum SentimentType {
        POSITIVE,NEGATIVE,NEUTRAL
    }

	public Long getId() {
		return id;
	}

	public void setId(Long id) {
		this.id = id;
	}

	public String getContent() {
		return content;
	}

	public void setContent(String content) {
		this.content = content;
	}

	public Double getSentimentScore() {
		return sentimentScore;
	}

	public void setSentimentScore(Double sentimentScore) {
		this.sentimentScore = sentimentScore;
	}

	public LocalDateTime getCreatedAt() {
		return createdAt;
	}

	public void setCreatedAt(LocalDateTime createdAt) {
		this.createdAt = createdAt;
	}

	public SentimentType getSentiment() {
		return sentiment;
	}

	public void setSentiment(SentimentType sentiment) {
		this.sentiment = sentiment;
	}

	
}
