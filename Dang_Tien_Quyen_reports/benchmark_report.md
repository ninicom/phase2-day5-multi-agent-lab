# Benchmark Report: Single-Agent vs Multi-Agent

## 1. Trace Link
**LangSmith Trace**: Traces have been streamed automatically during execution. View the detailed execution timeline at: [https://smith.langchain.com/](https://smith.langchain.com/) (Requires login and valid `LANGSMITH_API_KEY`).

## 2. Benchmark Comparison
Below is the side-by-side performance comparison for the query: `"Test GraphRAG Benchmarking"`

| Metric | Single-Agent Baseline | Multi-Agent Workflow |
|---|---|---|
| **Latency** | 15.74s | 47.66s |
| **Estimated Cost** | $0.00032 | $0.00009 |
| **Quality Score** (LLM Judge) | 8.0 / 10 | 9.0 / 10 |
| **Errors** | 0 | 0 |

*Note: After enabling Tavily API Key, the Multi-Agent workflow reached out to the internet, grabbed real papers about GraphRAG-Bench, and generated a highly detailed report, pushing its Quality Score up to 9.0!*

## 3. Failure Mode & Mitigation

**Failure Mode:**
Hệ thống có thể gặp lỗi treo (timeout) khi OpenAI API phản hồi chậm, hoặc các Agent gặp trạng thái lặp vô hạn (infinite loop) khi Supervisor đưa ra dự đoán kém và không chịu trả về giá trị `done`, dẫn đến việc cứ liên tục chuyển quyền giữa `researcher` và `analyst`.

**Cách Fix (Đã áp dụng):**
1. **API Resilience**: Cần bổ sung `timeout` trong client HTTP (đã thêm `timeout=10.0` ở `SearchClient`). Với OpenAI, ta có thể dùng library `tenacity` (@retry) để auto-retry nếu mạng rớt.
2. **Infinite Loop Guard**: Đã bổ sung biến đếm vòng lặp `state.iteration` vào `ResearchState` và triển khai câu lệnh check `state.iteration >= settings.max_iterations` ngay phần đầu của `SupervisorAgent`. Nếu số bước vượt quá định mức cho phép, hệ thống sẽ tự ép `next_node = "done"` để kết thúc workflow, tránh bị "đốt" sạch ngân sách token.
