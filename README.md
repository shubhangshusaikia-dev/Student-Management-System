# Student Management System

A professional desktop Student Management System built with **Python**, **CustomTkinter**, and **SQLite**. It provides a clean interface for creating, searching, updating, and deleting student records.

## Features

- Modern CustomTkinter desktop UI with light, dark, and system themes.
- SQLite database created automatically on first launch.
- Add, edit, delete, and browse student records.
- Search students by name, email, phone, or course.
- Validation for required fields, email format, and ISO date fields.
- Duplicate email protection through a database uniqueness constraint.

## Project Structure

```text
.
├── database.py       # SQLite schema and repository operations
├── main.py           # CustomTkinter user interface
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
```

## Getting Started

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python main.py
   ```

The app stores data in `students.db`, which is generated in the project directory when the application starts.

## Student Fields

- First name
- Last name
- Email
- Phone
- Gender
- Date of birth
- Course
- Enrollment date
- Address
