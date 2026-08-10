# StudyTrack — Enterprise Full-Stack Study Management & AI Platform (v2.0)

StudyTrack is an internal Trainee Enablement platform engineered for Myntra. It unifies a live Student/Course roster management backend, a hand-rolled algorithms engine with benchmark tracking and execution tracing, and an integrated AI vector search assistant — all accessible from a single, running web application.

---

## 🏛️ Repository & Architecture Layout

```
studytrack/
├── backend/
│   ├── main.py           # FastAPI application, route declarations, CORS, performance middleware
│   ├── database.py       # SQLAlchemy engine, sessionmaker, Base configuration
│   ├── models.py         # Student and Course ORM database models
│   ├── schemas.py        # Pydantic request/response schemas with field validation
│   ├── crud.py           # Database CRUD operations and SQL aggregate count query
│   ├── algorithms.py     # Part 2 hand-rolled Insertion Sort, Binary Search, Traces & Reports
│   ├── ai_service.py     # Part 3 Note Summarizer, 12-vocab Mock Embed & Cosine Similarity
│   ├── seed_data.py      # Part 2 exact seed dataset & automatic startup seeding
│   └── requirements.txt  # Backend dependencies
├── frontend/
│   ├── index.html        # HTML5 semantic dashboard layout, Toast engine, Course Modal
│   ├── style.css         # Dark glassmorphism styling, box-model spacing, responsive media query
│   └── app.js            # DOM creation, event delegation on #roster-list, keyboard shortcuts
├── .env.example          # Environment variable template
├── .gitignore            # Git ignore file excluding secrets, DB, and virtual environments
└── README.md             # Complete system documentation, setup, and complexity write-up
```

---

## 🚀 Run Mode & Setup Instructions

StudyTrack operates under the **Single-Process Run Mode** (Recommended). The FastAPI backend serves both the REST API endpoints and mounts the `frontend/` directory as static files at the root URL `/`.

### Prerequisites
- Python 3.9+ installed.

### Setup Steps
1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd studytrack
   ```

2. **Create and Activate Virtual Environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Start the Application**:
   ```bash
   python -m uvicorn backend.main:app --reload --port 8000
   ```

5. **Access the Dashboard & API Docs**:
   - **Web Dashboard**: Open `http://localhost:8000/` in any browser.
   - **Interactive API Documentation (Swagger UI)**: Open `http://localhost:8000/docs`.

---

## 📋 Part 1 — Core App Documentation

### API Endpoints Summary

| Method | Endpoint Path | Request Body | Description & Response Shape |
| :--- | :--- | :--- | :--- |
| `POST` | `/students/` | `{"name": "...", "email": "...", "age": int}` | Creates a new student record (201). Returns `StudentResponse`. |
| `GET` | `/students/` | *Optional query: `?min_age=20`* | Returns array of `StudentResponse` filtered by minimum age. |
| `GET` | `/students/{student_id}` | None | Fetches single student record (404 if missing). |
| `PATCH` | `/students/{student_id}`| `{"age": 23}` | Partially updates student record. Returns updated `StudentResponse`. |
| `DELETE`| `/students/{student_id}`| None | Deletes student record (204 No Content, 404 if missing). |
| `GET` | `/students/{student_id}/course-count` | None | Returns `{"student_id": int, "course_count": int}` computed via SQL aggregate. |
| `POST` | `/courses/` | `{"course_name": "...", "credits": int, "student_id": int}` | Enrolls student in course (201). Returns `CourseResponse`. |
| `GET` | `/courses/` | None | Returns array of `CourseResponse`. |
| `GET` | `/courses/{course_id}` | None | Fetches single course record (404 if missing). |
| `PATCH` | `/courses/{course_id}` | `{"credits": 4}` | Partially updates course record. |
| `DELETE`| `/courses/{course_id}` | None | Deletes course record (204 No Content). |

### Validation & Database Aggregation Details
- **Email Validation**: Custom Pydantic validator (`validate_email_contains_at` in `schemas.py`) rejects any string missing an `@` character with a `422 Unprocessable Entity` error before touching the database. Duplicate emails trigger a database-level integrity check returned as `400 Bad Request`.
- **Age Constraint**: Enforced using Pydantic `Field(gt=0)` to reject zero or negative ages.
- **Credits Constraint**: Enforced using Pydantic `Field(ge=1, le=6)` and SQLAlchemy `CheckConstraint("credits >= 1 AND credits <= 6")`.
- **Database Course Count Aggregate**: In `crud.py`, `get_student_course_count(db, student_id)` executes a SQL aggregate query:
  ```python
  db.query(func.count(models.Course.id)).filter(models.Course.student_id == student_id).scalar()
  ```
  This performs a database-side `SELECT COUNT(*)` aggregation rather than loading rows into Python.

### Frontend Dashboard Features
- **Semantic HTML & Glassmorphism Styling**: Built with semantic `<header>`, `<main>`, `<section>`, and `<footer>` elements.
- **CSS Box Model & Responsive Design**: Explicit padding, margin, and borders are applied to `#roster-list` and individual cards (`.student-card`). The `@media (max-width: 600px)` media query switches student cards to a single column layout on smaller screens.
- **DOM Element Creation**: Cards are built using `document.createElement()` and appended to the DOM (no list-wide string concatenation).
- **Event Delegation**: A single click listener is attached to `#roster-list`. It inspects `event.target.dataset.action` to handle "Save Age" (PATCH request), "Delete Student" (DELETE request), and "+ Enroll Course" modal triggers.
- **Toast Notifications & Error Handling**: Toast alert system handles UI notifications, while on-page `#error-banner` handles network/server errors.

---

## ⚡ Part 2 — Integrated Algorithms Engine

All algorithm functions reside in `backend/algorithms.py`.

### Seed Dataset
The app automatically seeds the database on initial startup with the 8 exact student records:
Aditi Rao (22), Rohan Mehta (19), Kavya Nair (25), Farhan Sheikh (18), Priya Iyer (21), Devansh Gupta (23), Meera Joshi (20), and Sameer Khan (24).

### Implemented Algorithms
1. **Hand-Written Insertion Sort (`insertion_sort_by_field`)**:
   - Endpoint: `GET /students/sorted?by=age` (or `by=name`).
   - Sorts student dicts ascending in-place without calling built-in `sorted()` or `.sort()`.
   - Result on seeded dataset (`by=age`): Farhan Sheikh (18), Rohan Mehta (19), Meera Joshi (20), Priya Iyer (21), Aditi Rao (22), Devansh Gupta (23), Sameer Khan (24), Kavya Nair (25).
2. **Hand-Written Iterative Binary Search (`binary_search_by_name`)**:
   - Endpoint: `GET /students/search?name=Priya Iyer`.
   - Sorts roster alphabetically by name first using Python's `sorted()`, then executes iterative binary search using `mid = low + (high - low) // 2`.
   - Searching "Priya Iyer" returns her full student record. Searching a non-existent name returns `404 Not Found`.
3. **Roster Report & Accumulator Counting**:
   - Endpoint: `GET /students/report?min_age=21`.
   - `format_roster_report(students)` builds multi-line formatted string: `[Age {age}] {name} <{email}>`.
   - `count_students_meeting_min_age(students, min_age)` counts students with `age >= min_age` using an explicit loop with an accumulator variable `count = 0`. Returns `count_meeting_min_age: 5` for `min_age=21`.

### 📝 Algorithm Complexity Analysis

> **Insertion Sort Complexity**:
> Insertion Sort operates by dividing the array into sorted and unsorted regions, taking elements one by one from the unsorted region and inserting them into their correct position in the sorted region. In the **worst-case scenario** (when the input array is sorted in reverse order), every element must be shifted past every previously processed element. This results in $1 + 2 + \dots + (n-1) = \frac{n(n-1)}{2}$ comparisons and shifts, yielding an $O(n^2)$ time complexity. In contrast, in the **best-case scenario** (when the array is already sorted), the inner `while` loop condition (`students[j][field] > key_val`) evaluates to `False` on the very first comparison for every element. Thus, Insertion Sort only performs $n-1$ comparisons and 0 shifts, achieving a linear time complexity of $O(n)$.

> **Binary Search Precondition**:
> Binary Search requires the input dataset to be sorted on the target comparison field prior to execution. This requirement stems from the fundamental divide-and-conquer strategy of the algorithm: at each iteration, Binary Search calculates a midpoint and compares the midpoint's value against the target search key. Because of the monotonic ordering property guaranteed by a sorted list ($A[i] \le A[j]$ for all $i < j$), comparing the target to the midpoint allows the algorithm to deterministically eliminate half of the remaining search space. If the array were unsorted, a comparison at the midpoint would provide no structural guarantee about which half of the array contains the target element, causing Binary Search to incorrectly discard valid data.

---

## 🤖 Part 3 — Integrated AI Assistant

All AI assistant modules reside in `backend/ai_service.py` and are accessible via the **AI Helper** sidebar panel in the dashboard.

### 1. Note Summarizer
- Endpoint: `POST /assistant/summarize` (Body: `{"text": "<raw study notes>"}`).
- **Deterministic Mock Mode Rules**:
  - `topic`: Extracted from the first title-like line or most frequent non-trivial word (falls back to `"untitled"` for empty input).
  - `key_points`: Up to 3 sentences split on `.!?` and stripped of whitespace (`[]` for empty input).
  - `difficulty`: Evaluated based on word count thresholds (`< 40` words $\rightarrow$ `"easy"`, `40–100` words $\rightarrow$ `"medium"`, `> 100` words $\rightarrow$ `"hard"`).
  - Edge Case: Calling `summarize_notes("")` or `summarize_notes(" ")` returns `{"topic": "untitled", "key_points": [], "difficulty": "easy"}` without throwing an exception.

#### Real LLM Prompting Design (Documentation)
If `AI_MODE=real` were enabled, the structured system prompt sent to an LLM provider would be:
```text
SYSTEM PROMPT:
You are an expert AI Study Assistant for Myntra's Trainee Enablement team.
Your task is to analyze raw study notes provided by a student and summarize them into a structured JSON object.

CONSTRAINTS & FORMAT INSTRUCTIONS:
- You MUST respond with valid JSON and ONLY valid JSON matching this exact schema:
  {
    "topic": "string (brief 2-5 word title of the main subject)",
    "key_points": ["array of 1 to 3 key takeaway sentence strings"],
    "difficulty": "string (strictly one of: 'easy', 'medium', or 'hard')"
  }
- Difficulty rating rules:
  - 'easy': introductory concepts, simple definitions, short text under 40 words.
  - 'medium': standard procedural explanations, moderate length (40-100 words).
  - 'hard': complex algorithms, multi-step technical workflows, text over 100 words.
- Do not include markdown code block backticks (e.g. ```json), commentary, or extra keys.

USER INPUT:
{raw_text}
```

### 2. Mock Embedding & Cosine Similarity Semantic Search
- Endpoint: `GET /assistant/search?query=binary search algorithm`.
- **Vocabulary & Embedding**: `mock_embed(text)` tokenizes text using lowercase regex `\w+` and calculates exact match frequencies against a fixed 12-word vocabulary: `["sort", "search", "binary", "insertion", "sql", "join", "fastapi", "pydantic", "prompt", "llm", "database", "validate"]`. It returns a 12-element numerical vector.
- **Cosine Similarity**: Hand-written in `cosine_similarity(vec_a, vec_b)` using dot product divided by vector magnitudes (`math.sqrt`).
- **Zero-Vector Safety**: If either vector has an L2 magnitude of `0.0` (e.g. empty or out-of-vocabulary query like `"xyz zzz"`), `cosine_similarity` returns `0.0` directly without raising a `ZeroDivisionError`.
- **Sample Dataset**: The 5 study notes are embedded and ranked descending by similarity score. An empty or out-of-vocabulary query returns all 5 notes with score `0.0` in their original order.

### Grading Mode Declaration
This project is configured and graded using **Deterministic Mock Mode** (`AI_MODE=mock`). It operates 100% offline with zero external network calls or paid API keys required.

---

## 🔀 Git Workflow Verification

This repository was developed using feature branch workflows.
To view the branch creation, multi-commit history, and merge graph, run:
```bash
git log --graph --oneline --all
```
The output shows feature branch `feature/core-and-algorithms` with multiple commits merged back into `main`.
