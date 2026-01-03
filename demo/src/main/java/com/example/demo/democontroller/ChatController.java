package com.example.demo.democontroller;

import java.util.Map;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/api")
public class ChatController {

    private final ChatClient chatClient;

    public ChatController(ChatClient.Builder chatClientBuilder) {
        this.chatClient = chatClientBuilder.build();
    }


    @GetMapping("/chat")
    public String chat(@RequestParam("message") String message) {
        return chatClient.prompt(message).call().content();
    }

    @GetMapping("/RAGchat")
    public String RAGchat(@RequestParam("text") String text) {
    	// 1. Define the URL of the Flask container (using the mapped port)
        String flaskUrl = "http://localhost:8007/RAGchat"; 
        
        // 2. Prepare the Request Body (JSON payload)
        String jsonBody = String.format("{\"question\": \"%s\"}", text);

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

        return response.getBody().get("answer").toString().toUpperCase();
    }
    
}
