package com.example.demo.democontroller;

import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.example.demo.demoservice.OllamaSpeechService;

@RestController
@RequestMapping("/api")
public class AudioController {

	private final OllamaSpeechService speechService;

    public AudioController(OllamaSpeechService speechService) {
        this.speechService = speechService;
    }
	
    @PostMapping("/transcribe")
	public String transcribe(@RequestPart("file") MultipartFile file) throws Exception {
        return speechService.transcribe(file);
    }
	
    @PostMapping("/speech")
    public ResponseEntity<byte[]> speech(@RequestBody String text) {
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_TYPE, "audio/wav")
                .body(speechService.getWavFromFlask(text));
    }

}
