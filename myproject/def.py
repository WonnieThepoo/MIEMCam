from flask import Flask, request
from ONVIFCameraControl import ONVIFCameraControl as OCC
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json


def get_cameras_list():
    SCOPES = ['https://www.googleapis.com/auth/admin.directory.resource.calendar.readonly',
                  'https://www.googleapis.com/auth/admin.directory.resource.calendar']
    SERVICE_ACCOUNT_FILE = 'visca.json'
    with open('gsuit.txt') as file:
        GSUIT_DOMAIN_ACCOUNT = file.readline()

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    delegated_credentials = credentials.with_subject(GSUIT_DOMAIN_ACCOUNT)
    service = build('admin', 'directory_v1', credentials=delegated_credentials)
    results = service.resources().calendars().list(customer='C03s7v7u4').execute()
    cameras = filter(lambda el: el['resourceType'] == 'ONVIF-camera', results['items'])
    return cameras

print(get_cameras_list())
