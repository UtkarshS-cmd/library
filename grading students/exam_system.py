# exam_system.py — College Exam and Grading System
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from datetime import date
import json
from pathlib import Path


# ─── Abstract Base: the contract every exam must honour ────────────
class BaseExam(ABC):
    """
    All exam types — MCQ, Descriptive, Practical — must implement
    grade() and full_marks(). This is the contract.
    """

    def __init__(self, exam_id: str, subject: str, duration_mins: int):
        self.exam_id = exam_id
        self.subject = subject
        self.duration_mins = duration_mins

    @abstractmethod
    def grade(self, answers: dict) -> float:
        """Grade an attempt. Returns marks obtained."""
        ...

    @abstractmethod
    def full_marks(self) -> int:
        """Total possible marks for this exam."""
        ...

    def percentage(self, obtained: float) -> float:
        """Concrete helper — shared by ALL exam types."""
        return (obtained / self.full_marks()) * 100

    def letter_grade(self, obtained: float) -> str:
        """Concrete helper — maps % to letter grade (Anna University scale)."""
        pct = self.percentage(obtained)
        if pct >= 90:
            return "O"  # Outstanding
        if pct >= 80:
            return "A+"
        if pct >= 70:
            return "A"
        if pct >= 60:
            return "B+"
        if pct >= 50:
            return "B"
        if pct >= 40:
            return "C"
        return "F"  # Fail

    def grade_point(self, obtained: float) -> float:
        """Maps letter grade to grade point (10-point scale)."""
        gp_map = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "F": 0}
        return gp_map[self.letter_grade(obtained)]

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.exam_id}: {self.subject},{self.full_marks()} marks)"


# ─── Concrete: MCQ Exam ────────────────────────────────────────────
class MCQExam(BaseExam):
    """
    Multiple Choice Question exam.
    Each correct answer: +marks_per_q
    Each wrong answer: -negative_marks (Indian competitive exam style)
    """

    def __init__(
        self,
        exam_id: str,
        subject: str,
        duration_mins: int,
        question_count: int,
        marks_per_q: float = 1.0,
        negative_marks: float = 0.25,
    ):
        super().__init__(exam_id, subject, duration_mins)
        self.question_count = question_count
        self.marks_per_q = marks_per_q
        self.negative_marks = negative_marks
        self._answer_key: dict[int, str] = {}  # question_no → correct option

    def set_answer_key(self, key: dict[int, str]) -> None:
        self._answer_key = key

    def full_marks(self) -> int:
        return int(self.question_count * self.marks_per_q)

    def grade(self, answers: dict) -> float:
        """
        answers = {1: "A", 2: "C", 3: "B", ...}
        Returns marks obtained (cannot go below 0).
        """
        if not self._answer_key:
            raise ValueError("Answer key not set. Call set_answer_key() first.")
        score = 0.0
        for qno, student_ans in answers.items():
            if qno not in self._answer_key:
                continue
            if student_ans == self._answer_key[qno]:
                score += self.marks_per_q
            else:
                score -= self.negative_marks
        return max(0.0, score)  # score cannot be negative


# ─── Concrete: Descriptive Exam ────────────────────────────────────
class DescriptiveExam(BaseExam):
    """
    Written descriptive exam — common in Indian universities.
    Has multiple sections (Part A, Part B), each with a max mark.
    Examiner enters marks per section.
    """

    def __init__(
        self, exam_id: str, subject: str, duration_mins: int, sections: dict[str, int]
    ):
        super().__init__(exam_id, subject, duration_mins)
        self._sections = sections  # e.g. {"Part A": 20, "Part B": 30}

    def full_marks(self) -> int:
        return sum(self._sections.values())

    def grade(self, answers: dict) -> float:
        """
        answers = {"Part A": 17, "Part B": 25} — marks per section
        Validates that no section exceeds its maximum.
        """
        total = 0.0
        for section, max_marks in self._sections.items():
            obtained = answers.get(section, 0)
            if obtained > max_marks:
                raise ValueError(f"{section}: {obtained} exceeds max {max_marks}")
            total += obtained
        return total


# ─── Practical Exam ────────────────────────────────────────────────
class PracticalExam(BaseExam):
    """Lab/practical exam — graded on execution, viva, and record."""

    def __init__(self, exam_id: str, subject: str, duration_mins: int):
        super().__init__(exam_id, subject, duration_mins)
        self._components = {"execution": 40, "viva": 30, "record": 30}

    def full_marks(self) -> int:
        return sum(self._components.values())

    def grade(self, answers: dict) -> float:
        total = 0.0
        for component, max_m in self._components.items():
            got = answers.get(component, 0)
            if got > max_m:
                raise ValueError(f"{component} exceeds max {max_m}")
            total += got
        return total


# ─── ExamResult dataclass ──────────────────────────────────────────
@dataclass
class ExamResult:
    exam: BaseExam
    obtained: float
    attempt_date: date = field(default_factory=date.today)

    @property
    def letter_grade(self) -> str:
        return self.exam.letter_grade(self.obtained)

    @property
    def grade_point(self) -> float:
        return self.exam.grade_point(self.obtained)

    @property
    def percentage(self) -> float:
        return self.exam.percentage(self.obtained)

    def __str__(self) -> str:
        return (
            f"{self.exam.subject}: {self.obtained}/{self.exam.full_marks()} "
            f"({self.percentage:.1f}%) - {self.letter_grade}"
        )


# ─── Student ───────────────────────────────────────────────────────
class Student:
    def __init__(self, roll_number: str, name: str, branch: str):
        self.roll_number = roll_number
        self.name = name
        self.branch = branch
        self._results: list[ExamResult] = []

    def add_result(self, result: ExamResult) -> None:
        self._results.append(result)

    @property
    def cgpa(self) -> float:
        """Calculate CGPA from all results."""
        if not self._results:
            return 0.0
        return sum(r.grade_point for r in self._results) / len(self._results)

    def print_transcript(self) -> None:
        print(f"\n{'='*55}")
        print(f" TRANSCRIPT - {self.name} ({self.roll_number})")
        print(f" Branch: {self.branch}")
        print(f"{'='*55}")
        for r in self._results:
            print(f" {r}")
        print(f"{'-'*55}")
        print(f" CGPA: {self.cgpa:.2f}")
        print(f"{'='*55}")

    def __str__(self) -> str:
        return f"Student({self.roll_number}: {self.name}, CGPA {self.cgpa:.2f})"


# ─── ExamSystem: Coordinates everything ────────────────────────────
class ExamSystem:
    """
    Orchestrates students and exams.
    Demonstrates polymorphism: conduct_exam() works with
    MCQExam, DescriptiveExam, or PracticalExam — same interface.
    """

    def __init__(self, university: str):
        self.university = university
        self._students: dict[str, Student] = {}
        self._exams: dict[str, BaseExam] = {}

    def register_student(self, student: Student) -> None:
        self._students[student.roll_number] = student
        print(f"Registered: {student.name}")

    def add_exam(self, exam: BaseExam) -> None:
        self._exams[exam.exam_id] = exam
        print(f"Added exam: {exam}")

    def conduct_exam(self, roll_number: str, exam_id: str, answers: dict) -> ExamResult:
        """
        Polymorphism here: exam.grade(answers) works whether
        exam is MCQExam, DescriptiveExam, or PracticalExam.
        ExamSystem does not know or care about the exam type.
        """
        student = self._students.get(roll_number)
        exam = self._exams.get(exam_id)
        if not student:
            raise ValueError(f"Student not found: {roll_number}")
        if not exam:
            raise ValueError(f"Exam not found: {exam_id}")
        obtained = exam.grade(answers)  # POLYMORPHIC CALL
        result = ExamResult(exam, obtained)
        student.add_result(result)
        print(f" {student.name} | {exam.subject}: {result}")
        return result

    def topper_report(self) -> None:
        """Print ranked student list by CGPA."""
        students = sorted(self._students.values(), key=lambda s: s.cgpa, reverse=True)
        print(f"\n=== {self.university} - Topper List ===")
        for i, s in enumerate(students, 1):
            print(f" {i}. {s.name:<20} CGPA: {s.cgpa:.2f} ({s.branch})")


# ─── Demo ──────────────────────────────────────────────────────────
def main():
    system = ExamSystem("VTU Belagavi")
    # Register students
    system.register_student(Student("1VT21CS001", "Ayaan Kumar", "CSE"))
    system.register_student(Student("1VT21CS002", "Priya Sharma", "CSE"))
    system.register_student(Student("1VT21EC001", "Vikram Nair", "ECE"))

    # Create exams
    maths_mcq = MCQExam(
        "M101",
        "Engineering Mathematics",
        180,
        question_count=100,
        marks_per_q=1.0,
        negative_marks=0.25,
    )
    maths_mcq.set_answer_key({1: "A", 2: "C", 3: "B", 4: "D", 5: "A"})

    ds_written = DescriptiveExam(
        "CS201",
        "Data Structures",
        180,
        sections={"Part A": 30, "Part B": 40, "Part C": 30},
    )
    lab = PracticalExam("CS202L", "Data Structures Lab", 180)

    system.add_exam(maths_mcq)
    system.add_exam(ds_written)
    system.add_exam(lab)

    # Conduct exams — same conduct_exam() works for all exam types
    print("\n--- Exam Results ---")
    system.conduct_exam("1VT21CS001", "M101", {1: "A", 2: "C", 3: "B", 4: "A", 5: "A"})
    system.conduct_exam(
        "1VT21CS001", "CS201", {"Part A": 25, "Part B": 35, "Part C": 28}
    )
    system.conduct_exam(
        "1VT21CS001", "CS202L", {"execution": 36, "viva": 25, "record": 28}
    )
    system.conduct_exam("1VT21CS002", "M101", {1: "A", 2: "D", 3: "B", 4: "D", 5: "C"})
    system.conduct_exam(
        "1VT21CS002", "CS201", {"Part A": 18, "Part B": 22, "Part C": 20}
    )

    # Transcripts
    for roll in ["1VT21CS001", "1VT21CS002"]:
        system._students[roll].print_transcript()

    # Rankings
    system.topper_report()


if __name__ == "__main__":
    main()
