import { useState, useEffect } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import axios from "axios";

function App() {
  const [feedback, setfeedback] = useState("");
  const [feedbackList, setFeedbackList] = useState([]);

  useEffect(() => {
    axios
      .get("http://localhost:8080/api/feedback")
      .then((response) => setFeedbackList(response.data))
      .catch((error) => console.error(error));
  }, []);

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();

    const response = await axios.post(
      "http://localhost:8080/api/feedback",
      feedback,
      {
        headers: { "Content-Type": "text/plain" },
      }
    );
    setFeedbackList([...feedbackList, response.data]);
    setfeedback("");
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case "POSITIVE":
        return "bg-green-100";
      case "NEGATIVE":
        return "bg-red-100";
      default:
        return "bg-gray-100";
    }
  };

  return (
    <>
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Sentiment Feedback Analyzer</h1>
        <form onSubmit={handleFeedbackSubmit} className="mb-4">
          <textarea
            value={feedback}
            onChange={(e) => setfeedback(e.target.value)}
            className="w-full p-2 border rounded  mb-2"
            placeholder="Enter the Feedback ..."
            rows="4"></textarea>
          <button
            type="submit"
            className="px-4 py-2 rounded bg-blue-600 text-white">
            Submit Feedback
          </button>
        </form>
        <h2 className="text-xl font-semibold mb-2">Feedback History</h2>
        <table className="table-auto w-full text-sm text-left text-gray-500">
          <thead className="text-gray-700 bg-gray-50">
            <tr>
              <th>Feedback</th>
              <th>Score</th>
              <th>Sentiment</th>
            </tr>
          </thead>
          <tbody>
            {feedbackList.map((item) => (
              <tr key={item.id}>
                <td>{item.content}</td>
                <td>{item.sentimentScore}</td>
                <td className={`${getSentimentColor(item.sentiment)}`}>
                  {item.sentiment}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default App;
