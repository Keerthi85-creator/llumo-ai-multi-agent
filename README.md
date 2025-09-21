# 📘 LLUMO Multi-Agent System

## 📌 Overview
This project implements a **multi-agent system** for handling user queries. The system:

- Accepts a natural-language query from the user.
- Plans solution steps (decides which tool to call).
- Routes the query to the correct tool.
- Executes tool calls with **timeouts, retries, and caching**.
- Produces a **final answer**.
- Logs every stage (`plan`, `tool_calls`, `critic`, `final`) into `logs.json`.

This follows the assignment specification and uses the provided `knowledgeBase.txt` as the information source.

---

## ⚙️ Requirements

- **Python 3.10+**

Install dependencies:

```bash
pip install -r requirements.txt
requirements.txt includes:
scikit-learn
numpy
```
---
🚀 How to Run
1. Interactive Mode

Start the agent and ask queries one by one:
```bash
python agent.py
```
---
You’ll see:
```bash
LLUMO Agent is ready! Type your query.
Type 'exit' or 'bye' to quit.
```
Example session:
```bash
>> What are the official working hours and overtime rules?
Answer: Standard working hours are 10:00 to 18:30 IST, Monday to Friday. Flexible timings are allowed with manager approval.

>> Compute: (125 * 6) - 50 and 15% of 640
Answer: (125 * 6) - 50 = 700; 15% of 640 = 96

>> bye
Goodbye 👋
```
---
📂 Project Structure
```bash
llumo-agent/
├─ agent.py                  # Main orchestrator
├─ knowledgeBase.txt         # Provided KB
├─ logs.json                 # Logs of interactions
├─ tools/
│  ├─ retriever.py           # TF-IDF retriever
│  ├─ calculator.py          # Safe math + natural language parsing
│  ├─ policy_lookup.py       # Policy-specific retriever
│  ├─ string_tools.py        # Regex-based helpers
├─ requirements.txt
├─ README.md
```
---
🔧 Tools & Logic
1. Planner

- Inspects the query and decides which tool to use.
Rules:

- Numbers + math symbols → Calculator

- Query mentions policy, hours, reimbursements → PolicyLookup

- Otherwise → Retriever

---

2. Retriever

- Uses TF-IDF vectorizer (via scikit-learn) over the KB.

- Returns top-k passages ranked by cosine similarity.
✅ Chosen because the KB is small and static → simple, interpretable, fast.

---

3. Calculator

- Uses Python ast to safely evaluate arithmetic expressions.

- Extended with parse_and_compute to handle:

- Natural language prefixes (e.g., "Compute:")

- Multiple expressions joined with "and"

- Percentages (e.g., "15% of 640" → (15/100)*640)

---

4. PolicyLookup

- Keyword + score-based matcher for queries about working hours, overtime, reimbursements.

- Returns the most relevant policy document from KB.

---

5. StringTools

- Extracts numbers and percentages using regex.
  
- Helps calculator pre-processing.

---

6. Executor

- Wraps every tool call with:

- Timeouts (via ThreadPoolExecutor)

- Retries (basic loop, exponential backoff)

- Caching (SHA256-hash based in-memory cache)

---

7. Critic

- Minimal check: validates if a final answer was produced.

- Can be extended with semantic validation.

---

8. Logging

- Produces structured JSON entries:

- plan → which tool(s) chosen

- tool_calls → inputs/outputs/errors

- critic → validation result

- final → query and answer

---

📝 Assumptions

- KB (knowledgeBase.txt) is trusted input and does not change during runtime.

- Queries are one at a time (interactive loop).

- Policy-related queries can be solved with keyword-based lookup (no embeddings needed).

- Only basic arithmetic and percentage math is expected.

- Logs are written in logs.json file
