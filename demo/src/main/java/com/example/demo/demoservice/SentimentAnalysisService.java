package com.example.demo.demoservice;

import com.example.demo.sentiment.entity.Feedback;

import java.util.Map;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

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
    
    public String getFeedbackResponse(String text) {
        // 1. Define the URL of the Flask container (using the mapped port)
        String flaskUrl = "http://localhost:8004/sentiment"; 
        
        // 2. Prepare the Request Body (JSON payload)
        String jsonBody = String.format("{\"text\": \"%s\"}", text);

        // 3. Set Headers (Expect audio/wav response)
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        // Crucial: Tell RestTemplate to expect binary data (byte[])
        RestTemplate restTemplate = new RestTemplate();
        
        HttpEntity<String> entity = new HttpEntity<>(jsonBody, headers);

        // 4. Execute the POST request
        ResponseEntity<Map> response = restTemplate.exchange(
                flaskUrl,
                HttpMethod.POST,
                entity,
                Map.class
        );

        if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
            return response.getBody().get("sentiment").toString().toUpperCase(); // POSITIVE / NEGATIVE
        }

        throw new RuntimeException("Failed to get sentiment");
    }
}
