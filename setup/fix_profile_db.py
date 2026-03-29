# fix_profile_db.py
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.environ["NOTION_API_KEY"])
PROFILE_DB_ID = os.environ["PROFILE_DB_ID"]

notion.databases.update(
    database_id=PROFILE_DB_ID,
    properties={
        "Target Role":     {"rich_text": {}},
        "Skills":          {"multi_select": {"options": []}},
        "Available Hours": {"number": {"format": "number"}},
        "Phase":           {"select": {"options": [
                               {"name": "Intern Hunting", "color": "blue"},
                               {"name": "Placement Prep", "color": "green"},
                               {"name": "Learning",       "color": "yellow"}
                           ]}}
    }
)

print("✅ Profile DB properties added.")