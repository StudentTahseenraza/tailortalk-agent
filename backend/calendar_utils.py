from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import dateutil.parser
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def check_availability(date: str, time_range: dict = None) -> list:
    service = get_calendar_service()
    try:
        target_date = dateutil.parser.parse(date).date()
    except:
        target_date = (datetime.now() + timedelta(days=1)).date()  # Default to tomorrow

    start_time = datetime.combine(target_date, datetime.time(9, 0))
    end_time = datetime.combine(target_date, datetime.time(17, 0))

    if time_range:
        try:
            start_time = datetime.combine(target_date, datetime.time.fromisoformat(time_range['start']))
            end_time = datetime.combine(target_date, datetime.time.fromisoformat(time_range['end']))
        except:
            raise ValueError("Invalid time range format")

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    slots = []
    current_time = start_time
    while current_time < end_time:
        slot_end = current_time + timedelta(minutes=30)
        if not any(
            datetime.fromisoformat(event['start']['dateTime'].replace('Z', '')) <= current_time and
            datetime.fromisoformat(event['end']['dateTime'].replace('Z', '')) >= slot_end
            for event in events
        ):
            slots.append(current_time.strftime("%H:%M"))
        current_time = slot_end
    return slots

def book_appointment(date: str, time: str, summary: str = "Meeting"):
    service = get_calendar_service()
    try:
        start_datetime = datetime.fromisoformat(f"{date}T{time}:00")
        end_datetime = start_datetime + timedelta(minutes=30)
        event = {
            'summary': summary,
            'start': {'dateTime': start_datetime.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': end_datetime.isoformat(), 'timeZone': 'UTC'}
        }
        service.events().insert(calendarId='primary', body=event).execute()
        return f"Booked appointment on {date} at {time}."
    except Exception as e:
        raise Exception(f"Failed to book appointment: {str(e)}")