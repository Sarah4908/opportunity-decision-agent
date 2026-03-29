# fix_opportunities_db.py
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.environ["NOTION_API_KEY"])
OPPORTUNITIES_DB_ID = os.environ["OPPORTUNITIES_DB_ID"]

notion.databases.update(
    database_id=OPPORTUNITIES_DB_ID,
    properties={
        "Type":            {"select": {"options": [
                               {"name": "Job"},
                               {"name": "Hackathon"},
                               {"name": "OA"},
                               {"name": "Other"}
                           ]}},
        "Skills Required": {"multi_select": {"options": []}},
        "Deadline Days":   {"number": {"format": "number"}},
        "Priority":        {"select": {"options": [
                               {"name": "High", "color": "red"},
                               {"name": "Medium", "color": "yellow"},
                               {"name": "Low", "color": "gray"}
                           ]}},
        "Action":          {"select": {"options": [
                               {"name": "Apply"},
                               {"name": "Prepare"},
                               {"name": "Consider"},
                               {"name": "Skip"}
                           ]}},
        "Confidence":      {"select": {"options": [
                               {"name": "High", "color": "green"},
                               {"name": "Medium", "color": "yellow"},
                               {"name": "Low", "color": "red"}
                           ]}},
        "Reason":          {"rich_text": {}},
        "Effort":          {"select": {"options": [
                               {"name": "Low"},
                               {"name": "Medium"},
                               {"name": "High"}
                           ]}}
    }
)

print("✅ Opportunities DB properties added.")