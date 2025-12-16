package com.example.demo.democontroller;

import java.util.List;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.demoservice.SentimentAnalysisService;
import com.example.demo.sentiment.entity.Feedback;
import com.example.demo.sentiment.entity.Feedback.SentimentType;
import com.example.demo.sentiment.repository.FeedbackRepository;

@RestController
@RequestMapping("/api/sentiment")
@CrossOrigin(origins = "http://localhost:5173/")
public class SentimentController {

	private final FeedbackRepository feedbackRepository;
    private final SentimentAnalysisService service;

    public SentimentController(FeedbackRepository feedbackRepository, SentimentAnalysisService service) {
    	this.feedbackRepository = feedbackRepository;
        this.service = service;
    }
	
    @GetMapping
    public List<Feedback> getAllFeedback() {
        return feedbackRepository.findAll();
    }
	
    @PostMapping
    public Feedback speech(@RequestBody String text) {
    	Feedback feedback = service.analyzeFeedback(text);
    	feedback.setSentiment(SentimentType.valueOf(service.getFeedbackResponse(text)));
        return feedbackRepository.save(feedback);
    }

}
