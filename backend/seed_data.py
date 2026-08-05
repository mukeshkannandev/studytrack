from sqlalchemy.orm import Session
from . import models

SEED_STUDENTS = [
    {"name": "Aditi Rao",     "email": "aditi.rao@example.com",     "age": 22},
    {"name": "Rohan Mehta",   "email": "rohan.mehta@example.com",   "age": 19},
    {"name": "Kavya Nair",    "email": "kavya.nair@example.com",    "age": 25},
    {"name": "Farhan Sheikh", "email": "farhan.sheikh@example.com", "age": 18},
    {"name": "Priya Iyer",    "email": "priya.iyer@example.com",    "age": 21},
    {"name": "Devansh Gupta", "email": "devansh.gupta@example.com", "age": 23},
    {"name": "Meera Joshi",   "email": "meera.joshi@example.com",   "age": 20},
    {"name": "Sameer Khan",   "email": "sameer.khan@example.com",   "age": 24},
]


def seed_if_empty(db: Session):
    existing_count = db.query(models.Student).count()
    if existing_count == 0:
        created_students = []
        for s_data in SEED_STUDENTS:
            student = models.Student(**s_data)
            db.add(student)
            created_students.append(student)
        db.commit()

        # Seed sample courses for demonstration of course-count endpoint
        if created_students:
            aditi = created_students[0] # Aditi Rao
            course1 = models.Course(course_name="Data Structures & Algorithms", credits=4, student_id=aditi.id)
            course2 = models.Course(course_name="Database Management Systems", credits=3, student_id=aditi.id)
            db.add_all([course1, course2])
            db.commit()
