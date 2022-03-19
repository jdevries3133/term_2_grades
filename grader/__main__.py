import logging

from .google_client import get_service

from .graders import week_20


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


def main():
    setup_logging()
    classroom, drive, slides = get_services()
    results = [*week_20(classroom, drive, slides)]
    breakpoint()


if __name__ == "__main__":
    main()
