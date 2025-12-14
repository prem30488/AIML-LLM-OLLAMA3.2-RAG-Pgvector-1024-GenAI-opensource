package com.example.demo.demoservice;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Base64;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

@Service
public class VisionService {

    private static final String OLLAMA_URL = "http://localhost:11434/api/generate";
    private static final String MODEL = "llama3.1-vision";    // supports vision + image generation

    private final HttpClient client = HttpClient.newHttpClient();

    // -------------------- IMAGE → TEXT --------------------
    public String imageToText(MultipartFile file) throws Exception {

        byte[] imageBytes = file.getBytes();
        String base64 = Base64.getEncoder().encodeToString(imageBytes);

        String prompt = "Describe the image in detail.";

        String json = """
        {
          "model": "%s",
          "prompt": "%s",
          "images": ["%s"],
          "stream": false
        }
        """.formatted(MODEL, prompt, base64);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(OLLAMA_URL))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();

        HttpResponse<String> response =
                client.send(request, HttpResponse.BodyHandlers.ofString());

        return response.body();   // JSON with "response"
    }


	 // Then, pass this hfToken string to your Python bridge/caller function.
 
    public byte[] textToImage(String text) throws Exception {

    	// 1. Define the URL of the Flask container (using the mapped port)
        String flaskUrl = "http://localhost:8001/tti"; 
        
        // 2. Prepare the Request Body (JSON payload)
        String jsonBody = String.format("{\"text\": \"%s\"}", text);

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
            // The byte array contains the JPEG file data
            return response.getBody(); 
        } else {
            throw new RuntimeException("Failed to get image data from DeepFloyd service. Status: " + response.getStatusCode());
        }
    }

}
