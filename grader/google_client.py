from copy import copy

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

from .utils import BASE_DIR, retry


class ClientWrapper:

    CREDENTIALS = BASE_DIR / "credentials.json"
    TOKEN = BASE_DIR / "temp" / "token.json"

    DEFAULT_SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/presentations.readonly",
        "openid",
        "https://www.googleapis.com/auth/classroom.courses.readonly",
        "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
        "https://www.googleapis.com/auth/classroom.student-submissions.students.readonly",
        "https://www.googleapis.com/auth/classroom.rosters.readonly",
        "https://www.googleapis.com/auth/classroom.profile.photos",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    def __init__(self, scopes=None):
        if scopes is None:
            scopes = copy(self.DEFAULT_SCOPES)

        self.scopes = scopes

    @retry(handle_exc=HttpError)
    def get_credentials(self) -> Credentials:

        credentials = None
        if self.TOKEN.exists():
            credentials = Credentials.from_authorized_user_file(self.TOKEN, self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDENTIALS, self.scopes
                )
                credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.TOKEN, "w") as token:
                token.write(credentials.to_json())

        return credentials

    @retry(handle_exc=HttpError)
    def get_service(self, service, version):
        credentials = self.get_credentials()
        return build(service, version, credentials=credentials)

    def download_google_slide_as_html(self, file_id) -> str:
        """This hacks together the private API to make it possible to export
        google slides as html"""

        # the source below is the gist of what needs to be done to use this
        # private API, but it doesn't quite work. I might revisit this, but
        # first, I am going to try to check for completion by downloading the
        # powerpowerpoint and using openpyxl
        raise NotImplemented
        tok = self.get_credentials().token
        uri = (
            f"https://docs.google.com/presentation/d/{file_id}/export/html"
            f"?id={file_id}"
            "&pageid=p"
            "&returnExportRedirectUrl=true"
            f"&token={tok}"
            "&includes_info_params=1"
            "&usp=drive_web"
        )

        response = requests.get(
            uri,
            headers={
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            },
        )
        return str(response.content, "utf8")


_client = ClientWrapper()


def get_service(service, version):
    return _client.get_service(service, version)


def slide_to_html(file_id) -> str:
    return _client.download_google_slide_as_html(file_id)
