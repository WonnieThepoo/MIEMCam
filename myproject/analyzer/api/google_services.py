from googleapiclient.discovery import build
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials


class GoogleAdminService:
    def __init__(self):
        SCOPES = ['https://www.googleapis.com/auth/admin.directory.resource.calendar.readonly',
              'https://www.googleapis.com/auth/admin.directory.resource.calendar']
        SERVICE_ACCOUNT_FILE = '../utils/visca.json'
        GSUIT_DOMAIN_ACCOUNT = 'ankurkin@miem.hse.ru'

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
             SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        delegated_credentials = credentials.create_delegated(GSUIT_DOMAIN_ACCOUNT)
        self.service = build('admin', 'directory_v1', credentials=delegated_credentials)

    def get(self):
        a = []
        results = self.service.resources().calendars().list(customer='C03s7v7u4').execute()
        for i in results['items']:
            if i['resourceType'] == 'ONVIF-camera':
                a.append(i)
        return a


