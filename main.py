"""Professional Student Management System built with CustomTkinter and SQLite."""

from __future__ import annotations

import re
import sqlite3
from datetime import date
from tkinter import messagebox, ttk

import customtkinter as ctk

from database import Student, StudentRepository

EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}$")
COURSES = [
    "Computer Science",
    "Information Technology",
    "Business Administration",
    "Engineering",
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
]
GENDERS = ["Female", "Male", "Non-binary", "Prefer not to say"]


class StudentManagementApp(ctk.CTk):
    """Main desktop application window."""

    def __init__(self) -> None:
        super().__init__()
        self.repository = StudentRepository()
        self.selected_student_id: int | None = None
        self.entries: dict[str, ctk.CTkEntry | ctk.CTkTextbox | ctk.CTkComboBox] = {}

        self.title("Student Management System")
        self.geometry("1180x720")
        self.minsize(1050, 650)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self._configure_grid()
        self._build_header()
        self._build_form()
        self._build_table_panel()
        self.refresh_students()

    def _configure_grid(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Student Management System",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.grid(row=0, column=0, padx=24, pady=(18, 2), sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Manage student admissions, contact details, courses, and enrollment records.",
            text_color=("gray35", "gray75"),
        )
        subtitle.grid(row=1, column=0, padx=24, pady=(0, 18), sticky="w")

        self.appearance = ctk.CTkOptionMenu(
            header,
            values=["System", "Light", "Dark"],
            command=ctk.set_appearance_mode,
            width=120,
        )
        self.appearance.grid(row=0, column=1, rowspan=2, padx=24, pady=18)

    def _build_form(self) -> None:
        form = ctk.CTkFrame(self)
        form.grid(row=1, column=0, padx=20, pady=20, sticky="ns")

        ctk.CTkLabel(form, text="Student Profile", font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=18, pady=(18, 12), sticky="w"
        )

        fields = [
            ("first_name", "First Name"),
            ("last_name", "Last Name"),
            ("email", "Email"),
            ("phone", "Phone"),
            ("date_of_birth", "Date of Birth (YYYY-MM-DD)"),
            ("enrollment_date", "Enrollment Date (YYYY-MM-DD)"),
        ]
        for row, (key, label) in enumerate(fields, start=1):
            self._add_entry(form, row, key, label)

        self._add_combo(form, 7, "gender", "Gender", GENDERS)
        self._add_combo(form, 8, "course", "Course", COURSES)

        ctk.CTkLabel(form, text="Address").grid(row=9, column=0, padx=18, pady=(10, 2), sticky="w")
        address = ctk.CTkTextbox(form, width=330, height=82)
        address.grid(row=10, column=0, columnspan=2, padx=18, pady=(0, 10), sticky="ew")
        self.entries["address"] = address

        button_frame = ctk.CTkFrame(form, fg_color="transparent")
        button_frame.grid(row=11, column=0, columnspan=2, padx=18, pady=(8, 18), sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(button_frame, text="Save Student", command=self.save_student).grid(
            row=0, column=0, padx=(0, 6), pady=5, sticky="ew"
        )
        ctk.CTkButton(button_frame, text="Clear Form", fg_color="gray45", command=self.clear_form).grid(
            row=0, column=1, padx=(6, 0), pady=5, sticky="ew"
        )
        ctk.CTkButton(button_frame, text="Delete Selected", fg_color="#B42318", command=self.delete_student).grid(
            row=1, column=0, columnspan=2, pady=5, sticky="ew"
        )

    def _build_table_panel(self) -> None:
        panel = ctk.CTkFrame(self)
        panel.grid(row=1, column=1, padx=(0, 20), pady=20, sticky="nsew")
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        toolbar = ctk.CTkFrame(panel, fg_color="transparent")
        toolbar.grid(row=0, column=0, padx=18, pady=(18, 8), sticky="ew")
        toolbar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Search by name, email, phone, or course")
        self.search_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda _event: self.refresh_students())
        ctk.CTkButton(toolbar, text="Refresh", width=110, command=self.refresh_students).grid(row=0, column=1)

        self.count_label = ctk.CTkLabel(panel, text="0 students")
        self.count_label.grid(row=1, column=0, padx=18, pady=(0, 8), sticky="w")

        columns = ("id", "name", "email", "phone", "gender", "course", "enrolled")
        self.table = ttk.Treeview(panel, columns=columns, show="headings", selectmode="browse")
        headings = {
            "id": "ID",
            "name": "Student Name",
            "email": "Email",
            "phone": "Phone",
            "gender": "Gender",
            "course": "Course",
            "enrolled": "Enrolled",
        }
        widths = {"id": 55, "name": 180, "email": 210, "phone": 120, "gender": 120, "course": 170, "enrolled": 100}
        for column in columns:
            self.table.heading(column, text=headings[column])
            self.table.column(column, width=widths[column], anchor="w")
        self.table.grid(row=2, column=0, padx=18, pady=(0, 18), sticky="nsew")
        self.table.bind("<<TreeviewSelect>>", self.populate_form_from_selection)

        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=self.table.yview)
        scrollbar.grid(row=2, column=1, pady=(0, 18), sticky="ns")
        self.table.configure(yscrollcommand=scrollbar.set)

    def _add_entry(self, parent: ctk.CTkFrame, row: int, key: str, label: str) -> None:
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=18, pady=(7, 2), sticky="w")
        entry = ctk.CTkEntry(parent, width=330)
        entry.grid(row=row, column=1, padx=18, pady=(7, 2), sticky="ew")
        self.entries[key] = entry

    def _add_combo(self, parent: ctk.CTkFrame, row: int, key: str, label: str, values: list[str]) -> None:
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=18, pady=(7, 2), sticky="w")
        combo = ctk.CTkComboBox(parent, values=values, width=330, state="readonly")
        combo.set(values[0])
        combo.grid(row=row, column=1, padx=18, pady=(7, 2), sticky="ew")
        self.entries[key] = combo

    def get_form_student(self) -> Student:
        values: dict[str, str] = {}
        for key, widget in self.entries.items():
            if isinstance(widget, ctk.CTkTextbox):
                values[key] = widget.get("1.0", "end").strip()
            else:
                values[key] = widget.get().strip()
        return Student(id=self.selected_student_id, **values)

    def validate_student(self, student: Student) -> str | None:
        required = {
            "First name": student.first_name,
            "Last name": student.last_name,
            "Email": student.email,
            "Phone": student.phone,
            "Date of birth": student.date_of_birth,
            "Course": student.course,
            "Enrollment date": student.enrollment_date,
            "Address": student.address,
        }
        missing = [label for label, value in required.items() if not value]
        if missing:
            return f"Please complete: {', '.join(missing)}."
        if not EMAIL_PATTERN.match(student.email):
            return "Please enter a valid email address."
        for label, value in (("Date of birth", student.date_of_birth), ("Enrollment date", student.enrollment_date)):
            try:
                date.fromisoformat(value)
            except ValueError:
                return f"{label} must use YYYY-MM-DD format."
        return None

    def save_student(self) -> None:
        student = self.get_form_student()
        validation_error = self.validate_student(student)
        if validation_error:
            messagebox.showwarning("Validation Error", validation_error)
            return
        try:
            if self.selected_student_id is None:
                self.repository.create(student)
                messagebox.showinfo("Saved", "Student record created successfully.")
            else:
                self.repository.update(student)
                messagebox.showinfo("Updated", "Student record updated successfully.")
            self.clear_form()
            self.refresh_students()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Email", "A student with this email already exists.")

    def delete_student(self) -> None:
        if self.selected_student_id is None:
            messagebox.showwarning("No Selection", "Select a student to delete first.")
            return
        if not messagebox.askyesno("Confirm Delete", "Delete the selected student record?"):
            return
        self.repository.delete(self.selected_student_id)
        self.clear_form()
        self.refresh_students()

    def refresh_students(self) -> None:
        for item in self.table.get_children():
            self.table.delete(item)
        students = self.repository.all(self.search_entry.get() if hasattr(self, "search_entry") else "")
        for student in students:
            self.table.insert(
                "",
                "end",
                iid=str(student.id),
                values=(
                    student.id,
                    f"{student.first_name} {student.last_name}",
                    student.email,
                    student.phone,
                    student.gender,
                    student.course,
                    student.enrollment_date,
                ),
            )
        self.count_label.configure(text=f"{len(students)} student{'s' if len(students) != 1 else ''}")

    def populate_form_from_selection(self, _event: object | None = None) -> None:
        selected = self.table.selection()
        if not selected:
            return
        student_id = int(selected[0])
        student = next((item for item in self.repository.all() if item.id == student_id), None)
        if student is None:
            return
        self.selected_student_id = student.id
        values = student.__dict__
        for key, widget in self.entries.items():
            value = values[key]
            if isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")
                widget.insert("1.0", value)
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set(value)
            else:
                widget.delete(0, "end")
                widget.insert(0, value)

    def clear_form(self) -> None:
        self.selected_student_id = None
        for key, widget in self.entries.items():
            if isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set(GENDERS[0] if key == "gender" else COURSES[0])
            else:
                widget.delete(0, "end")
        self.table.selection_remove(self.table.selection())


if __name__ == "__main__":
    app = StudentManagementApp()
    app.mainloop()
