package com.example.demo.demoservice;

import com.example.demo.sentiment.entity.Feedback;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.stereotype.Service;

@Service
public class SentimentAnalysisService {

    private final ChatClient chatClient;

    public SentimentAnalysisService(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    public Feedback analyzeFeedback(String content) {

        String prompt = String.format("""
            Analyze the sentiment of the following text and respond with only one word: POSITIVE, NEUTRAL, or NEGATIVE.
            Also provide a sentiment score between -1 and 1 where:
            -1 is most negative
            0 is neutral
            1 is most positive
            
            Format the response as: SENTIMENT_TYPE|SCORE
            
            Text to analyze: %s
            """, content);

        String response = chatClient
                .prompt(prompt)
                .call()
                .content();

        System.out.println("response = " + response);

        String[] parts = response.split("\\|");

        Feedback feedback = new Feedback();
        feedback.setContent(content);
        feedback.setSentimentScore(Double.parseDouble(parts[1].trim()));
        feedback.setSentiment(Feedback.SentimentType.valueOf(parts[0].trim()));

        return feedback;
    }
}
