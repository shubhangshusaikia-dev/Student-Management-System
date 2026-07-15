"""SQLite data access layer for the Student Management System."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional

DATABASE_PATH = Path(__file__).with_name("students.db")


@dataclass(frozen=True)
class Student:
    """Represents a student record stored in SQLite."""

    id: Optional[int]
    first_name: str
    last_name: str
    email: str
    phone: str
    gender: str
    date_of_birth: str
    course: str
    enrollment_date: str
    address: str


class StudentRepository:
    """Repository that encapsulates all student database operations."""

    def __init__(self, db_path: Path = DATABASE_PATH) -> None:
        self.db_path = db_path
        self.initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    date_of_birth TEXT NOT NULL,
                    course TEXT NOT NULL,
                    enrollment_date TEXT NOT NULL,
                    address TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def all(self, search: str = "") -> list[Student]:
        query = """
            SELECT id, first_name, last_name, email, phone, gender,
                   date_of_birth, course, enrollment_date, address
            FROM students
        """
        parameters: Iterable[str] = ()
        if search:
            query += """
                WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?
                   OR phone LIKE ? OR course LIKE ?
            """
            like_term = f"%{search}%"
            parameters = (like_term, like_term, like_term, like_term, like_term)
        query += " ORDER BY last_name COLLATE NOCASE, first_name COLLATE NOCASE"

        with self.connect() as connection:
            rows = connection.execute(query, tuple(parameters)).fetchall()
            return [self._row_to_student(row) for row in rows]

    def create(self, student: Student) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO students (
                    first_name, last_name, email, phone, gender, date_of_birth,
                    course, enrollment_date, address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self._student_values(student),
            )
            return int(cursor.lastrowid)

    def update(self, student: Student) -> None:
        if student.id is None:
            raise ValueError("A student id is required for updates.")
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE students
                SET first_name = ?, last_name = ?, email = ?, phone = ?,
                    gender = ?, date_of_birth = ?, course = ?,
                    enrollment_date = ?, address = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*self._student_values(student), student.id),
            )

    def delete(self, student_id: int) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM students WHERE id = ?", (student_id,))

    @staticmethod
    def _student_values(student: Student) -> tuple[str, str, str, str, str, str, str, str, str]:
        return (
            student.first_name.strip(),
            student.last_name.strip(),
            student.email.strip().lower(),
            student.phone.strip(),
            student.gender.strip(),
            student.date_of_birth.strip(),
            student.course.strip(),
            student.enrollment_date.strip(),
            student.address.strip(),
        )

    @staticmethod
    def _row_to_student(row: sqlite3.Row) -> Student:
        return Student(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            phone=row["phone"],
            gender=row["gender"],
            date_of_birth=row["date_of_birth"],
            course=row["course"],
            enrollment_date=row["enrollment_date"],
            address=row["address"],
        )
