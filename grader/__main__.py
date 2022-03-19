import logging

from .google_client import get_service

from .graders import ClassroomGrader, GradeResult


class Week20And21Grader(ClassroomGrader):
    def grading_method(self, assignment):
        """is_slideshow_changed and is_form_submitted are generic grading
        methods built into ClassroomGrader. This method is responsible for
        dispatching."""

        assgt_name = assignment["title"]
        if "week 20" in assgt_name.lower():
            return self.is_slideshow_changed
        if "week 21" in assgt_name.lower():
            return self.is_form_submitted

        raise ValueError(f"there is no method for grading {assgt_name}")


def setup_logging():
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    logging.getLogger("grader").setLevel(logging.DEBUG)


def get_services():
    classroom = get_service("classroom", "v1")
    drive = get_service("drive", "v3")
    slides = get_service("slides", "v1")
    return classroom, drive, slides


def week_20(classroom, drive, slides) -> list[GradeResult]:
    grader = Week20And21Grader(
        {
            "classroom": classroom,
            "drive": drive,
            "slides": slides,
        },
        assignment_name="Week 20",
        match_classrooms=[r"[467]th Grade General Music"],
        match_assignments=[r"Week 20 Day \d Do-Now"],
    )
    return grader.grade_assignments()


def week_21(classroom) -> list[GradeResult]:
    classroom_helper = Week20And21Grader(
        {"classroom": classroom},
        assignment_name="Week 21",
        match_assignments=[r"Week 21 Day \d Do-Now"],
        match_classrooms=[r"[467]th Grade General Music"],
    )

    return classroom_helper.grade_assignments()


def main():
    setup_logging()
    classroom, drive, slides = get_services()
    results = [*week_20(classroom, drive, slides), *week_21(classroom)]
    breakpoint()


if __name__ == "__main__":
    main()
