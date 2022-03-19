from .google_client import get_service


drive = get_service("drive", "v3")
classroom = get_service("classroom", "v1")

from pprint import pprint

pprint(classroom.courses().list().execute())
pprint(drive.files().list().execute())
