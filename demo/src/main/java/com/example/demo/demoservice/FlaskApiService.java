package com.example.demo.demoservice;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;

import java.util.Map;

@Service
public class FlaskApiService {

    private static final String BASE_URL = "http://localhost:8008";
    private final RestTemplate restTemplate = new RestTemplate();

    public String searchAndScrape(String keyword, int maxResults) {
        String url = BASE_URL + "/ingest?keyword={keyword}&max_results={maxResults}";

        return restTemplate.getForObject(
                url,
                String.class,
                Map.of(
                        "keyword", keyword,
                        "maxResults", maxResults
                )
        );
    }

    public String ragQuery(String question) {
        String url = BASE_URL + "/rag-query";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> body = Map.of("question", question);
        HttpEntity<Map<String, String>> request =
                new HttpEntity<>(body, headers);

        return restTemplate.postForObject(url, request, String.class);
    }
    
    public String stockPredict(String topic ,String symbol) {
        String url = BASE_URL + "/run-alerts";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> body = Map.of("topic", topic, "symbol",symbol);
        HttpEntity<Map<String, String>> request =
                new HttpEntity<>(body, headers);

        return restTemplate.postForObject(url, request, String.class);
    }
}
