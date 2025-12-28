package com.example.demo.demoservice;

import java.util.function.Consumer;

import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.client.WebClient;

import reactor.core.publisher.Mono;

@Service
public class OllamaSpeechService {
	
	private final RestTemplate restTemplate = new RestTemplate();
	
	public class MultipartBodyBuilderHelper {
	    public static Mono<MultiValueMap<String, HttpEntity<?>>> build(
	            Consumer<MultipartBodyBuilder> consumer) {
	        MultipartBodyBuilder builder = new MultipartBodyBuilder();
	        consumer.accept(builder);
	        return Mono.just(builder.build());
	    }
	}

    private final WebClient webClient;

    public OllamaSpeechService(WebClient.Builder builder) {
        this.webClient = builder
                .baseUrl("http://localhost:10300") // Ollama server
                .build();
    }

    public String transcribe(MultipartFile audio) throws Exception {

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("audio", new ByteArrayResource(audio.getBytes()) {
            @Override
            public String getFilename() {
                return audio.getOriginalFilename();
            }
        });

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        HttpEntity<MultiValueMap<String, Object>> request =
                new HttpEntity<>(body, headers);

        ResponseEntity<String> response =
                restTemplate.postForEntity(
                        "http://localhost:8006/transcribe",
                        request,
                        String.class
                );

        return response.getBody();
    }

    // ... inside your service or controller

    public byte[] getWavFromFlask(String text) {
        // 1. Define the URL of the Flask container (using the mapped port)
        String flaskUrl = "http://localhost:8000/tts"; 
        
        // 2. Prepare the Request Body (JSON payload)
        String jsonBody = String.format("{\"text\": \"%s\",\"voice\":\"ljspeech\"}", text);

        // 3. Set Headers (Expect audio/wav response)
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        // Crucial: Tell RestTemplate to expect binary data (byte[])
        RestTemplate restTemplate = new RestTemplate();
        
        HttpEntity<String> entity = new HttpEntity<>(jsonBody, headers);

        // 4. Execute the POST request
        ResponseEntity<byte[]> response = restTemplate.exchange(
            flaskUrl,
            HttpMethod.POST,
            entity,
            byte[].class // Expect the raw binary data (byte array)
        );

        if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
            // The byte array contains the WAV file data
            return response.getBody(); 
        } else {
            throw new RuntimeException("Failed to get WAV data from TTS service.");
        }
    }
}
