package com.example.demo.democontroller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.demoservice.FlaskApiService;

@RestController
@RequestMapping("/api")
public class WebSearchController {
	private final FlaskApiService flaskApiService;

    public WebSearchController(FlaskApiService flaskApiService) {
        this.flaskApiService = flaskApiService;
    }

    @GetMapping("/search")
    public String search(@RequestParam String keyword) {
        return flaskApiService.searchAndScrape(keyword, 5);
    }

    @PostMapping("/ask")
    public String ask(@RequestBody String question) {
        return flaskApiService.ragQuery(question);
    }
    
    @PostMapping("/stock-predict")
    public String stockPredict(@RequestParam String topic ,@RequestParam String symbol ) {
        return flaskApiService.stockPredict(topic, symbol);
    }
}
