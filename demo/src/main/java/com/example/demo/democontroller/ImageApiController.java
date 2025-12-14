package com.example.demo.democontroller;

import java.io.IOException;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api")
public class ImageApiController {

    private final RestTemplate restTemplate = new RestTemplate();
    private final String PYTHON_SERVER = "http://localhost:8002";  
    // Change to Docker container host if needed

    // ================================
    // 1️⃣ CAPTION WRAPPER
    // ================================
    @PostMapping("/caption")
    public ResponseEntity<String> caption(@RequestParam("image") MultipartFile file)
            throws IOException {

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        HttpEntity<byte[]> fileEntity =
                new HttpEntity<>(file.getBytes(), createFileHeaders(file.getOriginalFilename()));

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("image", fileEntity);

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        String url = PYTHON_SERVER + "/caption";

        ResponseEntity<String> response =
                restTemplate.postForEntity(url, requestEntity, String.class);

        return ResponseEntity.status(response.getStatusCode()).body(response.getBody());
    }


    // ================================
    // 2️⃣ OCR WRAPPER
    // ================================
    @PostMapping("/ocr")
    public ResponseEntity<String> ocr(@RequestParam("image") MultipartFile file)
            throws IOException {

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        HttpEntity<byte[]> fileEntity =
                new HttpEntity<>(file.getBytes(), createFileHeaders(file.getOriginalFilename()));

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("image", fileEntity);

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        String url = PYTHON_SERVER + "/ocr";

        ResponseEntity<String> response =
                restTemplate.postForEntity(url, requestEntity, String.class);

        return ResponseEntity.status(response.getStatusCode()).body(response.getBody());
    }


    // Helper: Builds multipart headers for each file
    private HttpHeaders createFileHeaders(String filename) {
        HttpHeaders fileHeaders = new HttpHeaders();
        fileHeaders.setContentType(MediaType.IMAGE_JPEG);
        fileHeaders.setContentDispositionFormData("image", filename);
        return fileHeaders;
    }
}
