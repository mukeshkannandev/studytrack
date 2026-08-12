import os
import time
import logging
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import engine, Base, get_db
from . import models, schemas, crud, algorithms, ai_service, seed_data

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("studytrack")

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyTrack Platform API",
    description="Enterprise Trainee Enablement Service with Integrated Algorithms Engine and AI Vector Assistant",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Custom Middleware for Performance Tracking & Request Metrics
@app.middleware("http")
async def add_performance_headers_and_log(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.3f}"
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({process_time_ms:.2f}ms)")
    return response

# CORS Configuration (Strictly explicit origins, no wildcard "*")
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Handler with Automatic Seeding
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    try:
        seed_data.seed_if_empty(db)
        logger.info("Database initialized and verified with seed dataset.")
    finally:
        db.close()

# Custom Exception Handler for Database Integrity Conflicts
@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    logger.error(f"Database Integrity Error on {request.url.path}: {str(exc.orig)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Database Integrity Constraint Error: Duplicate email address or foreign key violation."}
    )

# ==========================================
# PART 1: CORE STUDENT & COURSE CRUD ENDPOINTS
# ==========================================

@app.post("/students/", response_model=schemas.StudentResponse, status_code=status.HTTP_201_CREATED, tags=["Students CRUD"])
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    existing = crud.get_student_by_email(db, student.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A student with this email address already exists."
        )
    return crud.create_student(db=db, student=student)


@app.get("/students/", response_model=List[schemas.StudentResponse], tags=["Students CRUD"])
def read_students(min_age: Optional[int] = Query(None, description="Filter students with age >= min_age"), db: Session = Depends(get_db)):
    return crud.get_students(db=db, min_age=min_age)


# IMPORTANT: Algorithm routes defined before /{student_id} to prevent routing collisions
@app.get("/students/sorted", tags=["Algorithms Engine"])
def get_sorted_students(
    by: str = Query("age", description="Sort field: 'age' or 'name'"),
    include_metrics: bool = Query(False, description="Return algorithm benchmark execution metrics"),
    db: Session = Depends(get_db)
):
    if by not in ["age", "name"]:
        raise HTTPException(status_code=400, detail="Query parameter 'by' must be 'age' or 'name'.")

    students_orm = crud.get_students(db=db)
    students_dicts = [
        {"id": s.id, "name": s.name, "email": s.email, "age": s.age} for s in students_orm
    ]

    if include_metrics:
        # Enhanced path: returns benchmark data alongside sorted results
        start_time = time.perf_counter()
        # Work on a copy so the base sort below is unaffected
        dicts_copy = [d.copy() for d in students_dicts]
        sorted_copy, comparisons, shifts = algorithms.insertion_sort_by_field_with_metrics(dicts_copy, field=by)
        exec_time_ms = (time.perf_counter() - start_time) * 1000
        return {
            "algorithm": "Insertion Sort",
            "field": by,
            "execution_time_ms": round(exec_time_ms, 4),
            "comparisons": comparisons,
            "shifts": shifts,
            "time_complexity": {"best_case": "O(n)", "worst_case": "O(n^2)"},
            "data": sorted_copy
        }

    # Default path: calls insertion_sort_by_field() directly as required
    sorted_list = algorithms.insertion_sort_by_field(students_dicts, field=by)
    return sorted_list


@app.get("/students/search", tags=["Algorithms Engine"])
def search_student_by_name(
    name: str = Query(..., description="Exact student name to search"),
    include_metrics: bool = Query(False, description="Return binary search execution trace"),
    db: Session = Depends(get_db)
):
    students_orm = crud.get_students(db=db)
    students_dicts = [
        {"id": s.id, "name": s.name, "email": s.email, "age": s.age} for s in students_orm
    ]

    # Sort alphabetically by name first — required precondition for Binary Search
    sorted_by_name = sorted(students_dicts, key=lambda x: x["name"])

    if include_metrics:
        # Enhanced path: returns execution trace alongside result
        start_time = time.perf_counter()
        result_trace, iterations, trace = algorithms.binary_search_by_name_with_trace(sorted_by_name, name)
        exec_time_ms = (time.perf_counter() - start_time) * 1000
        if result_trace == -1:
            raise HTTPException(status_code=404, detail=f"Student with name '{name}' not found.")
        return {
            "algorithm": "Iterative Binary Search",
            "searched_name": name,
            "found": True,
            "execution_time_ms": round(exec_time_ms, 4),
            "iterations": iterations,
            "search_trace": trace,
            "time_complexity": "O(log n)",
            "data": result_trace
        }

    # Default path: calls binary_search_by_name() directly as required
    result = algorithms.binary_search_by_name(sorted_by_name, name)
    if result == -1:
        raise HTTPException(status_code=404, detail=f"Student with name '{name}' not found.")
    return result


@app.get("/students/report", tags=["Algorithms Engine"])
def get_roster_report(min_age: int = Query(21, description="Minimum age threshold"), db: Session = Depends(get_db)):
    students_orm = crud.get_students(db=db)
    students_dicts = [
        {"id": s.id, "name": s.name, "email": s.email, "age": s.age} for s in students_orm
    ]
    report_str = algorithms.format_roster_report(students_dicts)
    count = algorithms.count_students_meeting_min_age(students_dicts, min_age=min_age)
    return {
        "report": report_str,
        "count_meeting_min_age": count
    }


@app.get("/students/{student_id}", response_model=schemas.StudentResponse, tags=["Students CRUD"])
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    return db_student


@app.patch("/students/{student_id}", response_model=schemas.StudentResponse, tags=["Students CRUD"])
def update_student(student_id: int, student_data: schemas.StudentUpdate, db: Session = Depends(get_db)):
    db_student = crud.update_student(db, student_id=student_id, student_data=student_data)
    if db_student is None:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    return db_student


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Students CRUD"])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    success = crud.delete_student(db, student_id=student_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    return None


@app.get("/students/{student_id}/course-count", response_model=schemas.StudentCourseCountResponse, tags=["Students CRUD"])
def get_student_course_count(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    count = crud.get_student_course_count(db, student_id=student_id)
    return {"student_id": student_id, "course_count": count}


@app.post("/courses/", response_model=schemas.CourseResponse, status_code=status.HTTP_201_CREATED, tags=["Courses CRUD"])
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id=course.student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Referenced Student with ID {course.student_id} not found.")
    return crud.create_course(db=db, course=course)


@app.get("/courses/", response_model=List[schemas.CourseResponse], tags=["Courses CRUD"])
def read_courses(db: Session = Depends(get_db)):
    return crud.get_courses(db=db)


@app.get("/courses/{course_id}", response_model=schemas.CourseResponse, tags=["Courses CRUD"])
def read_course(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail=f"Course with ID {course_id} not found")
    return db_course


@app.patch("/courses/{course_id}", response_model=schemas.CourseResponse, tags=["Courses CRUD"])
def update_course(course_id: int, course_data: schemas.CourseUpdate, db: Session = Depends(get_db)):
    db_course = crud.update_course(db, course_id=course_id, course_data=course_data)
    if db_course is None:
        raise HTTPException(status_code=404, detail=f"Course with ID {course_id} not found")
    return db_course


@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Courses CRUD"])
def delete_course(course_id: int, db: Session = Depends(get_db)):
    success = crud.delete_course(db, course_id=course_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Course with ID {course_id} not found")
    return None


# ==========================================
# PART 3: INTEGRATED AI ASSISTANT ENDPOINTS
# ==========================================

class SummarizeRequest(schemas.BaseModel):
    text: str


@app.post("/assistant/summarize", tags=["AI Assistant"])
def summarize_notes_endpoint(request: SummarizeRequest):
    return ai_service.summarize_notes(request.text)


@app.get("/assistant/search", tags=["AI Assistant"])
def search_notes_endpoint(
    query: str = Query("", description="Semantic vector search query over study notes")
):
    return ai_service.search_notes(query)


# ==========================================
# STATIC FILES MOUNT (SINGLE-PROCESS MODE)
# ==========================================

frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
