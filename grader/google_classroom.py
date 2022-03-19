import re
import logging

from teacherhelper import Helper


helper = Helper.read_cache()
logger = logging.getLogger(__name__)


class GoogleClassroom:
    def __init__(
        self,
        classroom_service,
        drive_service,
        match_assignments: list[str],
        match_classrooms: list[str] = None,
    ):
        self.classroom = classroom_service
        self.drive = drive_service
        self._match_pats = match_classrooms or []
        self._match_assgt = match_assignments or []

        # mapping of assignment ids to their html content, to avoid repetitive
        # google drive exports
        # TODO: implement me!
        self._teacher_content_cache = {}

    def get_classrooms(self) -> list[dict]:
        """Return the classrooms that match self._match_pats.

        Returns a list of courseId's that correspond to those classrooms.
        """
        courses = self.classroom.courses().list().execute()
        return self._filter_courses(courses)

    def _filter_courses(self, courses):
        ret = []
        for c in courses["courses"]:
            for p in self._match_pats:
                if re.search(p, c["name"]) is not None:
                    ret.append(c)

        return ret

    def get_assignments(self, course) -> list[dict]:
        assignments = (
            self.classroom.courses().courseWork().list(courseId=course["id"]).execute()
        )
        while token := assignments.get("nextPageToken") is not None:
            assignments += (
                self.classroom.courses()
                .courseWork()
                .list(courseId=course, nextPageToken=token)
                .execute()
            )
        return self._filter_assignments(assignments)

    def _filter_assignments(self, assignments):
        ret = []
        for c in assignments["courseWork"]:
            for p in self._match_assgt:
                if re.search(p, c["title"]) is not None:
                    ret.append(c)
        return ret

    def get_submissions(self, assignment):
        submissions = (
            self.classroom.courses()
            .courseWork()
            .studentSubmissions()
            .list(courseWorkId=assignment["id"], courseId=assignment["courseId"])
            .execute()
        )
        while token := submissions.get("nextPageToken") is not None:
            submissions += (
                self.classroom.courses()
                .courseWork()
                .studentSubmissions()
                .list(
                    courseWorkId=assignment["id"],
                    courseId=assignment["courseId"],
                    nextPageToken=token,
                )
                .execute()
            )
        return submissions["studentSubmissions"]

    def download_file(self, file_id: str, mime_type: str = "text/html"):
        return self.drive.files().export(fileId=file_id, mimeType=mime_type).execute()

    def traverse_submissions(self):
        """Yields current classroom, assignment, and submission resource
        while traversing all courseWorkSubmission according to configuration
        on initialization."""
        for classroom in self.get_classrooms():
            for assignment in self.get_assignments(classroom):
                for submission in self.get_submissions(assignment):
                    yield classroom, assignment, submission

    def get_content(self, assignment, file, mime_type="text/plain") -> tuple[str, str]:
        """For a given assignment, return the content of a submission for a
        given attachment. This returns a tuple of the teacher content, then
        the student content."""
        # impl: KeyErrors might bubble up

        student_content = self.download_file(
            file["driveFile"]["id"],
        )

        original_assignment = (
            self.classroom.courses()
            .courseWork()
            .get(courseId=assignment["courseId"], id=assignment["courseWorkId"])
            .execute()
        )

        # if there is only one attachment on the original, we don't need to do
        # any finegaling
        n_att = len(original_assignment["materials"])
        if n_att == 0:
            raise ValueError("original assignment has no attachments")
        if n_att == 1:
            teacher_content = self.download_file(
                original_assignment["materials"][0]["driveFile"]["driveFile"]["id"],
                mime_type,
            )
            return teacher_content, student_content

        # google classroom uses the naming convention:
        #     <student name> - <original file name>
        # <original file name> should therefore be a substring of the student
        # file's file name
        filename = file["driveFile"]["title"]

        for attachment in original_assignment["materials"]:
            if attachment["driveFile"]["title"] in filename:
                teacher_content = self.download_file(
                    attachment["driveFile"]["id"], mime_type
                )
                return teacher_content, student_content

        raise ValueError(f"could not get content for assignment {assignment}")
