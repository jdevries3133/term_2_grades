"""Client to get manual grades from classfast."""

import logging

from requests.sessions import Session
from teacherhelper import Helper

from .google_client import get_credentials, get_service
from .entities import GradeResult


logger = logging.getLogger(__name__)

classroom = get_service("classroom", "v1")


helper = Helper.read_cache()


# I just run this script against the development build running on my laptop so
# I can easily patch bugs and make data changes as I go
BASE_URI = "https://beta.classfast.app"


# primary keys of the grading sessions we need.
PKS = [3, 4, 5, 6]


def authenticate() -> Session:
    creds = get_credentials()
    session = Session()

    res = session.post(
        f"{BASE_URI}/accounts/dj_rest_auth/google/", {"access_token": creds.token}
    )
    if not res.ok:
        raise Exception("could not authenticate")
    return session


def week_19() -> list[GradeResult]:
    """Technically, this also gets wk 20 for grade 5."""
    retval: list[GradeResult] = []
    session = authenticate()
    for pk in PKS:
        res = session.get(f"{BASE_URI}/grader/deep_session/{pk}/")
        assignment = res.json()
        for submission in assignment["submissions"]:
            name = submission["student_name"]
            student = helper.find_nearest_match(name)  # type: ignore
            if student is None:
                logger.warning("no match for %s. dropping result", name)
                continue
            retval.append(
                GradeResult(
                    student=student,
                    assignment="week 20" if student.grade_level == 5 else "week 19",
                    grade=submission["grade"],
                )
            )

    logger.info("finished getting week 19 grades")

    return retval
