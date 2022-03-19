from dataclasses import dataclass
from typing import Literal

from teacherhelper.entities import Student


@dataclass
class GradeResult:
    student: Student
    assignment: Literal["week 20", "week 21"]
    grade: Literal[20, 15, 10, 0]
