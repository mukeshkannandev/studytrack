import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import engine, Base, get_db
from . import models, schemas, crud, algorithms, ai_service, seed_data

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyTrack API",
    description="Unified Full-Stack Study Management Platform with Integrated Algorithms Engine and AI Assistant",
    version="1.0.0",
)

# CORS configuration explicitly allowing frontend dev port 5500 (never wildcard '*')
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


@app.on_event("startup")
def startup_event():
    # Seed database if empty
    db = next(get_db())
    try:
        seed_data.seed_if_empty(db)
    finally:
        db.close()


# ==========================================
# PART 1: CORE STUDENT & COURSE CRUD ENDPOINTS
# ==========================================

@app.post("/students/", response_model=schemas.StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # Check duplicate email explicitly
    existing = crud.get_student_by_email(db, student.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A student with this email address already exists."
        )
    try:
        return crud.create_student(db=db, student=student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error: Duplicate email or constraint violation."
        )


@app.get("/students/", response_model=List[schemas.StudentResponse])
def read_students(min_age: Optional[int] = Query(None, description="Filter students with age >= min_age"), db: Session = Depends(get_db)):
    return crud.get_students(db=db, min_age=min_age)


# Note: Algorithms routes under /students/ must be defined before /students/{student_id} path parameter to prevent routing collisions
@app.get("/students/sorted")
def get_sorted_students(by: str = Query("age", description="Sort by field: 'age' or 'name'"), db: Session = Depends(get_db)):
    if by not in ["age", "name"]:
        raise HTTPException(status_code=400, detail="Query parameter 'by' must be 'age' or 'name'.")
    students_orm = crud.get_students(db=db)
    students_dicts = [
        {"id": s.id, "name": s.name, "email": s.email, "age": s.age} for s in students_orm
    ]
    sorted_list = algorithms.insertion_sort_by_field(students_dicts, field=by)
    return sorted_list


@app.get("/students/search")
def search_student_by_name(name: str = Query(..., description="Exact student name to search"), db: Session = Depends(get_db)):
    students_orm = crud.get_students(db=db)
    students_dicts = [
        {"id": s.id, "name": s.name, "email": s.email, "age": s.age} for s in students_orm
    ]
    # Algorithm requirement: sort alphabetically by name using Python built-in sorted() first
    sorted_by_name = sorted(students_dicts, key=lambda x: x["name"])
    result = algorithms.binary_search_by_name(sorted_by_name, name)
    if result == -1:
        raise HTTPException(status_code=404, detail=f"Student with name '{name}' not found.")
    return result


@app.get("/students/report")
def get_roster_report(min_age: int = Query(21, description="Minimum age filter for count"), db: Session = Depends(get_db)):
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


@app.get("/students/{student_id}", response_model=schemas.StudentResponse)
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student


@app.patch("/students/{student_id}", response_model=schemas.StudentResponse)
def update_student(student_id: int, student_data: schemas.StudentUpdate, db: Session = Depends(get_db)):
    db_student = crud.update_student(db, student_id=student_id, student_data=student_data)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    success = crud.delete_student(db, student_id=student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return None


@app.get("/students/{student_id}/course-count", response_model=schemas.StudentCourseCountResponse)
def get_student_course_count(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    count = crud.get_student_course_count(db, student_id=student_id)
    return {"student_id": student_id, "course_count": count}


@app.post("/courses/", response_model=schemas.CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id=course.student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Referenced Student with ID {course.student_id} not found.")
    return crud.create_course(db=db, course=course)


@app.get("/courses/", response_model=List[schemas.CourseResponse])
def read_courses(db: Session = Depends(get_db)):
    return crud.get_courses(db=db)


@app.get("/courses/{course_id}", response_model=schemas.CourseResponse)
def read_course(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course


@app.patch("/courses/{course_id}", response_model=schemas.CourseResponse)
def update_course(course_id: int, course_data: schemas.CourseUpdate, db: Session = Depends(get_db)):
    db_course = crud.update_course(db, course_id=course_id, course_data=course_data)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course


@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    success = crud.delete_course(db, course_id=course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return None


# ==========================================
# PART 3: INTEGRATED AI ASSISTANT ENDPOINTS
# ==========================================

class SummarizeRequest(schemas.BaseModel):
    text: str


@app.post("/assistant/summarize")
def summarize_notes_endpoint(request: SummarizeRequest):
    return ai_service.summarize_notes(request.text)


@app.get("/assistant/search")
def search_notes_endpoint(query: str = Query("", description="Query string to match notes via semantic vector similarity")):
    return ai_service.search_notes(query)


# ==========================================
# STATIC FILES MOUNT (SINGLE-PROCESS MODE)
# ==========================================

frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
