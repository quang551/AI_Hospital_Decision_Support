# AI-Based Intelligent Hospital Patient Scheduling and Prioritization System

Hệ thống AI điều phối và ưu tiên bệnh nhân trong bệnh viện.

## Description

Hệ thống mô phỏng việc tiếp nhận, ưu tiên và điều phối bệnh nhân trong bệnh viện.

AI sẽ phân tích thông tin bệnh nhân dựa trên Knowledge Base và các luật IF-THEN, sau đó sử dụng Forward Chaining để suy luận mức độ ưu tiên.

Kết quả được đưa vào Priority Queue và hệ thống sẽ sắp xếp lịch khám dựa trên bác sĩ, phòng và thời gian khả dụng.

## Technologies

- Python 3.11
- PySide6
- SQLite
- Pandas
- Matplotlib

## AI Algorithms

- Knowledge Representation
- Rule-Based Reasoning
- Forward Chaining
- Priority Scheduling

## Project Structure

```text
hospital_ai/
├── main.py
├── models/
├── knowledge/
├── scheduling/
├── database/
├── gui/
├── data/
└── tests/