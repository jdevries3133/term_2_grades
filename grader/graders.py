import logging
from typing import Literal

from teacherhelper import Helper

from .google_classroom import GoogleClassroom
from .entities import GradeResult


helper = Helper.read_cache()
logger = logging.getLogger(__name__)


class SlideGrader:
    def __init__(
        self,
        classroom_service,
        drive_service,
        slides_service,
        *,
        assignment_name,
        match_classrooms,
        match_assignments
    ):
        self.classroom = GoogleClassroom(
            classroom_service,
            drive_service,
            slides_service,
            match_classrooms=match_classrooms,
            match_assignments=match_assignments,
        )
        self.assignment_name = assignment_name

    def grade_slides_for_completion(self) -> list[GradeResult]:
        result_map = {}
        for _, assignment, submission in self.classroom.traverse_submissions():

            is_complete = self._is_slideshow_changed(submission)
            name = self.classroom.get_student_profile(submission)["name"]["fullName"]

            result_map.setdefault(name, {})
            result_map[name][assignment["title"]] = is_complete
            logger.debug(
                "{name} {status} complete {assignment_name}".format(
                    name=name,
                    status="did" if is_complete else "did not",
                    assignment_name=assignment["title"],
                )
            )

        retval: list[GradeResult] = []

        for name, result in result_map.items():
            n_complete = 0
            for is_complete in result.values():
                if is_complete:
                    n_complete += 1
            n_complete_to_grade: dict[int, Literal[0, 15, 20]] = {0: 0, 1: 15, 2: 20}
            retval.append(
                GradeResult(
                    student=helper.find_nearest_match(name),  # type: ignore
                    assignment=self.assignment_name,
                    grade=n_complete_to_grade[n_complete],
                )
            )

        return retval

    def _is_slideshow_changed(self, submission) -> bool:
        # ensure that there is exactly one attachment on the submission
        if "attachments" not in submission["assignmentSubmission"]:
            return False
        if len(submission["assignmentSubmission"]["attachments"]) < 1:
            return False
        elif len(submission["assignmentSubmission"]["attachments"]) != 1:
            logger.debug(submission)
            raise ValueError("can not grade. too many attachments")

        teacher, student = self.classroom.get_slides(
            submission,
            submission["assignmentSubmission"]["attachments"][0],
        )
        return teacher["slides"][1] != student["slides"][1]


def week_20(classroom, drive, slides) -> list[GradeResult]:
    grader = SlideGrader(
        classroom,
        drive,
        slides,
        assignment_name="Week 20",
        match_classrooms=[
            r"4th Grade General Music",
        ],
        match_assignments=[r"Week 20 Day \d Do-Now"],
    )
    return grader.grade_slides_for_completion()


def week_21(classroom, drive) -> list[GradeResult]:
    return []
