# Lab Guide: Multi-Agent Research System

## Scenario

Bạn cần xây dựng một research assistant có thể nhận câu hỏi dài, tìm thông tin, phân tích và viết câu trả lời cuối cùng. Lab yêu cầu so sánh hai cách làm:

1. **Single-agent baseline**: một agent làm toàn bộ.
2. **Multi-agent workflow**: Supervisor điều phối Researcher, Analyst, Writer.

## Quy tắc quan trọng

- Không thêm agent nếu không có lý do rõ ràng.
- Mỗi agent phải có responsibility riêng.
- Shared state phải đủ rõ để debug.
- Phải có trace hoặc log cho từng bước.
- Phải benchmark, không chỉ nhìn output bằng cảm tính.

## Milestone 1: Baseline

File gợi ý:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

TODO(student): thay baseline placeholder bằng một call LLM thật.

## Milestone 2: Supervisor

File gợi ý:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

TODO(student): implement routing policy.

Gợi ý câu hỏi thiết kế:

- Khi nào gọi Researcher?
- Khi nào gọi Analyst?
- Khi nào gọi Writer?
- Khi nào stop?
- Nếu agent fail thì retry hay fallback?

## Milestone 3: Worker agents

File gợi ý:

- `agents/researcher.py`
- `agents/analyst.py`
- `agents/writer.py`

TODO(student): implement từng worker.

## Milestone 4: Trace và benchmark

File gợi ý:

- `observability/tracing.py`
- `evaluation/benchmark.py`
- `evaluation/report.py`

Benchmark tối thiểu:

| Metric | Cách đo gợi ý |
|---|---|
| Latency | wall-clock time |
| Cost | token usage hoặc provider usage |
| Quality | rubric 0-10 do peer review |
| Citation coverage | số claims có source / tổng claims chính |
| Failure rate | số query fail / tổng query |

## Exit ticket

Mỗi nhóm trả lời 2 câu:

1. **Case nào nên dùng multi-agent? Vì sao?**
   - **Nên dùng khi:** Bài toán có độ phức tạp cao, đòi hỏi tư duy logic nhiều bước (như nghiên cứu tài liệu tổng hợp, viết code hệ thống lớn, kiểm toán tự động). 
   - **Vì sao:** Việc chia nhỏ thành nhiều Agent (chia để trị) giúp mỗi LLM prompt được tập trung (focus) vào đúng chuyên môn, giảm thiểu độ nhiễu context và hallucination. Hơn nữa, các Agent có thể review chéo kết quả của nhau (VD: Analyst kiểm tra lại Researcher) để đẩy mức Quality/Độ tin cậy lên cao nhất.

2. **Case nào không nên dùng multi-agent? Vì sao?**
   - **Không nên dùng khi:** Bài toán đơn giản, tra cứu nhanh, tóm tắt 1 văn bản, dịch thuật, hoặc các tính năng yêu cầu tốc độ phản hồi real-time cho user (như chatbot CSKH).
   - **Vì sao:** Đánh đổi của Multi-Agent là sự suy giảm mạnh về Tốc độ (Latency) và sự phình to của Chi phí (Cost). Qua benchmark, Multi-Agent mất thời gian và tiền bạc gấp 2.5 - 3 lần Single Agent chỉ vì việc hội thoại qua lại giữa các Node.
