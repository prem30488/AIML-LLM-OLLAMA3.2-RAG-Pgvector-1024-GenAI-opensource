package com.example.demo.demoservice;

import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

@Service
public class YoloClient {

    private static final String YOLO_URL =
            "http://localhost:8003/detect";

    private final RestTemplate restTemplate = new RestTemplate();

    public byte[] detect(byte[] imageBytes, String filename) {

        ByteArrayResource resource = new ByteArrayResource(imageBytes) {
            @Override
            public String getFilename() {
                return filename;
            }
        };

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("image", resource);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        HttpEntity<MultiValueMap<String, Object>> request =
                new HttpEntity<>(body, headers);

        ResponseEntity<byte[]> response =
                restTemplate.exchange(
                        YOLO_URL,
                        HttpMethod.POST,
                        request,
                        byte[].class
                );

        return response.getBody();
    }
}
