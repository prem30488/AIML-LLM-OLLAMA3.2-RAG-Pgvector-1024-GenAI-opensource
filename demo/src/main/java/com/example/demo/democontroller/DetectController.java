package com.example.demo.democontroller;

import com.example.demo.demoservice.CustomCNNService;
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
    private final CustomCNNService customCNNService;

    public DetectController(YoloClient yoloClient,CustomCNNService customCNNService) {
        this.yoloClient = yoloClient;
        this.customCNNService = customCNNService;
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
    
    @PostMapping("/classify")
    public ResponseEntity<byte[]> classify(
            @RequestParam("image") MultipartFile file
    ) throws Exception {

        byte[] result =
        		customCNNService.classify(file.getBytes(), file.getOriginalFilename());

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=result.jpg")
                .contentType(MediaType.IMAGE_JPEG)
                .body(result);
    }
}