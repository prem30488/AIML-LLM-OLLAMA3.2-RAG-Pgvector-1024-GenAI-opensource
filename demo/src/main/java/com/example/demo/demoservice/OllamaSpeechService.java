package com.example.demo.demoservice;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.UUID;
import java.util.function.Consumer;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Service;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.client.WebClient;

import reactor.core.publisher.Mono;

@Service
public class OllamaSpeechService {
	
	private static final String WHISPER_DIR = "D:/whisper/";
    private static final String WHISPER_EXE = "whisper.exe";

	
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

    public String transcribe(MultipartFile multipartFile) throws Exception {

        // Ensure folder exists
        Files.createDirectories(Paths.get(WHISPER_DIR));

        // Generate unique name
        String uniqueName = UUID.randomUUID().toString().replace("-", "");
        String mp3Path = WHISPER_DIR + uniqueName + ".mp3";
        String txtPath = WHISPER_DIR + uniqueName + ".txt";

        // Save MP3 file
        Path filePath = Paths.get(mp3Path);
        Files.copy(multipartFile.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);

        // Build command: whisper.exe "D:/whisper/xxxx.mp3"
        ProcessBuilder pb = new ProcessBuilder(
                WHISPER_EXE,
                filePath.toString()
        );

        pb.directory(new File(WHISPER_DIR));
        pb.redirectErrorStream(true);

        Process process = pb.start();

        // Read console output (optional but useful)
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()))) {

            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println("[WHISPER] " + line);
            }
        }

        // Wait for whisper.exe to complete
        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Whisper failed with exit code " + exitCode);
        }

        // Now read generated TXT file
        Path txtFilePath = Paths.get(txtPath);
        if (!Files.exists(txtFilePath)) {
            throw new FileNotFoundException("Output text file not found: " + txtPath);
        }

        return Files.readString(txtFilePath);
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
