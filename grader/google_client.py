from copy import copy
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .utils import BASE_DIR, retry


class ClientWrapper:

    CREDENTIALS = BASE_DIR / "credentials.json"
    TOKEN = BASE_DIR / "temp" / "token.json"

    DEFAULT_SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
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


_client = ClientWrapper()


def get_service(service, version):
    return _client.get_service(service, version)
