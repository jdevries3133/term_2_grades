import csv
from dataclasses import fields
import logging
from typing import cast, Literal

from teacherhelper.helper import Helper

from .classfast_client import week_19
from .google_client import get_service
from .graders import ClassroomGrader, GradeResult
from .doc_writer import DocWriter, Page


helper = Helper.read_cache()


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
        # this is the fifth grade assignment
        if assgt_name == "Week 20":
            return self.is_slideshow_changed

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
        assignment_name="week 20",
        match_classrooms=[r"[467]th Grade General Music"],
        match_assignments=[r"Week 20 Day \d Do-Now"],
    )
    results = grader.grade_assignments()
    print("finished getting week 20 results")
    return results


def week_21(classroom) -> list[GradeResult]:
    classroom_helper = Week20And21Grader(
        {"classroom": classroom},
        assignment_name="week 21",
        match_assignments=[r"Week 21 Day \d Do-Now"],
        match_classrooms=[r"[467]th Grade General Music"],
    )

    results = classroom_helper.grade_assignments()
    print("finished getting week 21 results")
    return results


def week_20_gr_5(classroom, drive, slides):
    grader = Week20And21Grader(
        {
            "classroom": classroom,
            "drive": drive,
            "slides": slides,
        },
        assignment_name="week 20",
        match_classrooms=[r"5th Grade General Music"],
        match_assignments=[r"Week 20"],
    )
    results = grader.grade_assignments()
    print("finished getting week 20 grade 5 results")
    return results


def main():
    setup_logging()
    classroom, drive, slides = get_services()
    results = [
        *week_19(),
        *week_20(classroom, drive, slides),
        *week_20_gr_5(classroom, drive, slides),
        *week_21(classroom),
    ]

    print("results fetched. finalizing now")

    mapping: dict[str, list[GradeResult]] = {}
    for r in results:
        mapping.setdefault(r.student.name, [])
        mapping[r.student.name].append(r)

    writer = DocWriter()
    homerooms = sorted(helper.homerooms.values(), key=lambda i: (i.grade_level, i.teacher))  # type: ignore
    all_pages = []
    for hr in homerooms:
        # a bit leaky but oh well
        writer.doc.add_page_break()
        writer.doc.add_heading(hr.teacher)

        pages = []
        for s in hr.students:
            student_results = mapping.get(s.name)
            if student_results is None:
                print("Student has no results: %s", s.name)
                pages.append(
                    Page(student=s.name, wk_19_grade=0, wk_20_grade=0, wk_21_grade=0)
                )
                continue

            assgt_to_result = {r.assignment: r.grade for r in student_results}

            page = Page(
                student=s.name,
                # cast grade, which we validate with assert statements below
                wk_19_grade=cast(
                    Literal[20, 15, 10, 0], assgt_to_result.get("week 19", 0)
                ),
                wk_20_grade=cast(Literal[20, 15, 0], assgt_to_result.get("week 20", 0)),
                wk_21_grade=cast(Literal[20, 15, 0], assgt_to_result.get("week 21", 0)),
            )
            if s.name == 'Michael Lee':
                breakpoint()

            try:
                assert page.wk_19_grade in (20, 15, 10, 0)
                assert page.wk_20_grade in (20, 15, 0)
                assert page.wk_21_grade in (20, 15, 0)
            except AssertionError:
                breakpoint()

            print(f"prepped page {page}")
            pages.append(page)
            all_pages.append(page)

        writer.add_pages(pages)
        print(f"homeroom {hr.teacher} complete")

    writer.doc.save("output.docx")
    with open("output.csv", "w") as fp:
        writer = csv.writer(fp)
        page_fields = fields(Page)
        writer.writerow(f.name for f in page_fields)
        writer.writerows(
            [getattr(page, f.name) for f in page_fields] for page in all_pages
        )


if __name__ == "__main__":
    main()
