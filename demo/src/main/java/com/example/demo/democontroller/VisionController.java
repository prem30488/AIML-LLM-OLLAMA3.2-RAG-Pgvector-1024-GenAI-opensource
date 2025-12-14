package com.example.demo.democontroller;

import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.example.demo.demoservice.VisionService;

@RestController
@RequestMapping("/api")
public class VisionController {

    private final VisionService visionService;

    public VisionController(VisionService visionService) {
        this.visionService = visionService;
    }

    // -------------------- IMAGE → TEXT --------------------
    @PostMapping(value = "/analyze", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<String> analyze(@RequestParam("image") MultipartFile file) throws Exception {
        return ResponseEntity.ok(visionService.imageToText(file));
    }

    // -------------------- TEXT → IMAGE --------------------
    @PostMapping(value = "/image", produces = MediaType.IMAGE_JPEG_VALUE)
    public ResponseEntity<byte[]> generate(@RequestBody String text) throws Exception {
        byte[] imageBytes = visionService.textToImage(text);
        return ResponseEntity.ok(imageBytes);
    }
}

