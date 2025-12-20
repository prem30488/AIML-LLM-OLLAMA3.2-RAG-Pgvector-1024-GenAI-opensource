package com.example.demo.democontroller;

import com.example.demo.demoservice.YoloClient;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api")
public class DetectController {

    private final YoloClient yoloClient;

    public DetectController(YoloClient yoloClient) {
        this.yoloClient = yoloClient;
    }

    @PostMapping("/detect")
    public ResponseEntity<byte[]> detect(
            @RequestParam("image") MultipartFile file
    ) throws Exception {

        byte[] result =
                yoloClient.detect(file.getBytes(), file.getOriginalFilename());

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=result.jpg")
                .contentType(MediaType.IMAGE_JPEG)
                .body(result);
    }
}