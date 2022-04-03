import csv
from difflib import ndiff
import logging
from typing import cast, Literal

import yaml

from grader.entities import Config

from .classfast_client import week_19
from .google_client import get_service
from .graders import ClassroomGrader, GradeResult
from .doc_writer import DocWriter, Page
from .teacherhelper_proxy import helper
from .utils import BASE_DIR


class Week20And21Grader(ClassroomGrader):
    def grading_method(self, assignment):
        """is_slideshow_changed and is_form_submitted are generic grading
        methods built into ClassroomGrader. This method is responsible for
        dispatching."""

        assgt_name = assignment["title"]
        # this is the fifth grade assignment
        if assgt_name == "Week 21":
            return self.is_slideshow_changed
        if "week 20" in assgt_name.lower():
            return self.is_slideshow_changed
        if "week 21" in assgt_name.lower():
            return self.is_form_submitted

        raise ValueError(f"there is no method for grading {assgt_name}")


def setup_logging():
    info = logging.FileHandler(filename="info.log")
    info.setLevel(logging.INFO)
    debug = logging.FileHandler(filename="debug.log")
    debug.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")

    console.setFormatter(formatter)
    debug.setFormatter(formatter)
    info.setFormatter(formatter)

    logging.getLogger("").addHandler(console)
    logging.getLogger("").addHandler(info)
    logging.getLogger("").addHandler(debug)

    logging.getLogger("grader").setLevel(logging.DEBUG)


def load_config() -> Config:
    with open(BASE_DIR / "config.yml", "r") as fp:
        data = yaml.safe_load(fp)
        return Config(**data)


def apply_grade_level_overrides(config: Config):
    """Applies grade-level overrides specified in overrides.yml"""
    matched = set()
    for s in helper.students.values():
        if level := config.grade_overrides.get(s.name):
            s.grade_level = level
            matched.add(s.name)

    # a bit of validation – we can make sure every override was matched by
    # asserting that every name is now in `matched`
    if not matched == (all_ := set(k for k in config.grade_overrides)):
        print(
            "Warning: not all grades were matched. "
            f"Differing elements: {matched.symmetric_difference(all_)}"
        )


def apply_grade_overrides(results: list[GradeResult], config: Config):
    """Apply grade overrides for single assignments. Does not handle overrides
    for total grades, because `list[GradeResult]` cannot propagage that
    information.

    This function mutates `results` in place.
    """
    for r in results:
        overrides = config.grade_overrides.get(r.student.name)
        if overrides and r.assignment in overrides:
            r.grade = overrides.get(r.assignment, r.grade)


def check_override(page: Page, config: Config):
    """set `Page.total_grade_override` if an override value was provided in
    the config.

    This function mutates `page` in place.
    """
    overrides = config.grade_overrides.get(page.student.name)
    if overrides is not None and 'total' in overrides:
        page.total_grade_override = overrides['total']


def apply_notes(page: Page, config: Config):
    """Add any notes specified in the config file to the page if provided.

    This function mutates `page` in place.
    """
    notes = config.notes.get(page.student.name)
    if notes is not None:
        if page.notes is None:
            page.notes = ''
        page.notes += '\n' + notes


def get_services():
    classroom = get_service("classroom", "v1")
    drive = get_service("drive", "v3")
    slides = get_service("slides", "v1")
    return classroom, drive, slides


def week_20(classroom, drive, slides) -> list[GradeResult]:
    """4th, 6th, and 7th grade do-now, which was a google slide"""
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
    """4th, 6th, and 7th grade do-now, which was a google form"""
    classroom_helper = Week20And21Grader(
        {"classroom": classroom},
        assignment_name="week 21",
        match_assignments=[r"Week 21 Day \d Do-Now"],
        match_classrooms=[r"[467]th Grade General Music"],
    )

    results = classroom_helper.grade_assignments()
    print("finished getting week 21 results")
    return results


def week_21_gr_5(classroom, drive, slides):
    """5th grade do-now, which was a goodle form"""
    grader = Week20And21Grader(
        {
            "classroom": classroom,
            "drive": drive,
            "slides": slides,
        },
        assignment_name="week 21",
        match_classrooms=[r"5th Grade General Music"],
        match_assignments=[r"Week 21"],
    )
    results = grader.grade_assignments()
    print("finished getting week 20 grade 5 results")
    return results


def main():
    setup_logging()
    config = load_config()
    apply_grade_level_overrides(config)
    classroom, drive, slides = get_services()
    print("starting grading")
    results = [
        *week_19(),
        *week_20(classroom, drive, slides),
        *week_21_gr_5(classroom, drive, slides),
        *week_21(classroom),
    ]

    apply_grade_overrides(results, config)

    print("results fetched. finalizing now")

    mapping: dict[str, list[GradeResult]] = {}
    for r in results:
        mapping.setdefault(r.student.name, [])
        mapping[r.student.name].append(r)

    writer = DocWriter()
    homerooms = sorted(helper.homerooms.values(), key=lambda i: (i.grade_level, i.teacher))  # type: ignore
    all_pages = []
    for hr in homerooms:
        if hr.grade_level == 5:
            continue

        # a bit leaky but oh well
        writer.doc.add_page_break()
        writer.doc.add_heading(hr.teacher)

        pages = []
        for s in hr.students:

            student_results = mapping.get(s.name)
            if student_results is None:
                print(f"Student has no results: {s.name}")
                pages.append(
                    Page(student=s, wk_19_grade=0, wk_20_grade=0, wk_21_grade=0)
                )
                continue

            assgt_to_result = {r.assignment: r.grade for r in student_results}

            page = Page(
                student=s,
                # cast grade, which we validate with assert statements below
                wk_19_grade=cast(
                    Literal[20, 15, 10, 0], assgt_to_result.get("week 19", 0)
                ),
                wk_20_grade=cast(Literal[20, 15, 0], assgt_to_result.get("week 20", 0)),
                wk_21_grade=cast(Literal[20, 15, 0], assgt_to_result.get("week 21", 0)),
            )
            check_override(page, config)
            apply_notes(page, config)

            try:
                assert page.wk_19_grade in (20, 15, 10, 0)
                assert page.wk_20_grade in (20, 15, 0)
                assert page.wk_21_grade in (20, 15, 0)
            except AssertionError:
                print(f"will not write invalid page: {page}")
                continue

            print(f"prepped page {page}")
            pages.append(page)
            all_pages.append(page)

        writer.add_pages(pages)
        print(f"homeroom {hr.teacher} complete")

    writer.doc.save("output.docx")
    with open("output.csv", "w") as fp:
        writer = csv.writer(fp)
        writer.writerow(("name", "w19", "w20", "w21", "total"))
        writer.writerows(
            [
                (
                    p.student.name,
                    p.wk_19_grade,
                    p.wk_20_grade,
                    p.wk_21_grade,
                    p.total_grade,
                )
                for p in all_pages
            ]
        )

    # TODO: not only should this be deduplicated, but I didn't implement the
    # override.yml for grade totals for the fifth grade. Right now, I don't
    # have any overrides at all for the fifth grade, so this is not urgent
    writer = DocWriter(type="fifth")
    all_pages = []
    for hr in homerooms:
        if hr.grade_level != 5:
            continue

        # a bit leaky but oh well
        writer.doc.add_page_break()
        writer.doc.add_heading(hr.teacher)

        pages = []
        for s in hr.students:
            student_results = mapping.get(s.name)
            if student_results is None:
                print(f"Student has no results: {s.name}")
                pages.append(
                    Page(student=s, wk_19_grade=0, wk_20_grade=0, wk_21_grade=0)
                )
                continue

            assgt_to_result = {r.assignment: r.grade for r in student_results}

            page = Page(
                student=s,
                wk_19_grade=0,  # this is internally dropped for fifth
                wk_20_grade=cast(
                    Literal[20, 15, 10, 0], assgt_to_result.get("week 20", 0)
                ),
                wk_21_grade=cast(Literal[20, 0], assgt_to_result.get("week 21", 0)),
            )
            check_override(page, config)
            apply_notes(page, config)

            try:
                assert page.wk_20_grade in (20, 15, 10, 0)
                assert page.wk_21_grade in (20, 0)
            except AssertionError:
                print(f"will not write invalid page: {page}")
                continue

            print(f"prepped page for {page.student.name}: {page}")
            pages.append(page)
            all_pages.append(page)

        writer.add_pages(pages)
        print(f"homeroom {hr.teacher} complete")

    writer.doc.save("output_fifth.docx")
    with open("output_fifth.csv", "w") as fp:
        writer = csv.writer(fp)
        writer.writerow(("name", "w20", "w21", "total"))
        writer.writerows(
            [
                (p.student.name, p.wk_20_grade, p.wk_21_grade, p.total_grade)
                for p in all_pages
            ]
        )


if __name__ == "__main__":
    main()
