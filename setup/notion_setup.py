# notion_setup.py
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.environ["NOTION_API_KEY"])

def get_or_create_databases():
    """Auto-creates both DBs on first run, loads them on subsequent runs."""
    
    # Search for existing databases
    results = notion.search().get("results", [])
    results = [r for r in results if r["object"] == "database"]
    
    existing = {db["title"][0]["plain_text"]: db["id"] for db in results if db.get("title")}
    
    profile_db_id = existing.get("User Profile")
    opportunities_db_id = existing.get("Opportunities")
    
    # Get the first page in workspace to use as parent
    pages = notion.search(filter={"property": "object", "value": "page"}).get("results", [])
    
    if not pages:
        print("❌ No pages found in Notion. Please create one page manually first.")
        exit()
    
    parent_page_id = pages[0]["id"]
    
    # Create User Profile DB if missing
    if not profile_db_id:
        print("📋 Creating User Profile database...")
        db = notion.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "User Profile"}}],
            properties={
                "Name":             {"title": {}},
                "Target Role":      {"rich_text": {}},
                "Skills":           {"multi_select": {"options": []}},
                "Available Hours":  {"number": {"format": "number"}},
                "Phase":            {"select": {"options": [
                                        {"name": "Intern Hunting", "color": "blue"},
                                        {"name": "Placement Prep", "color": "green"},
                                        {"name": "Learning",       "color": "yellow"}
                                    ]}}
            }
        )
        profile_db_id = db["id"]
        print("✅ User Profile DB created")
    else:
        print("✅ User Profile DB found")

    # Create Opportunities DB if missing
    if not opportunities_db_id:
        print("📋 Creating Opportunities database...")
        db = notion.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "Opportunities"}}],
            properties={
                "Title":            {"title": {}},
                "Type":             {"select": {"options": [
                                        {"name": "Job"},
                                        {"name": "Hackathon"},
                                        {"name": "OA"},
                                        {"name": "Other"}
                                    ]}},
                "Skills Required":  {"multi_select": {"options": []}},
                "Deadline Days":    {"number": {"format": "number"}},
                "Priority":         {"select": {"options": [
                                        {"name": "🔥 High", "color": "red"},
                                        {"name": "Medium",  "color": "yellow"},
                                        {"name": "Low",     "color": "gray"}
                                    ]}},
                "Action":           {"select": {"options": [
                                        {"name": "Apply"},
                                        {"name": "Prepare"},
                                        {"name": "Consider"},
                                        {"name": "Skip"}
                                    ]}},
                "Confidence":       {"select": {"options": [
                                        {"name": "High",   "color": "green"},
                                        {"name": "Medium", "color": "yellow"},
                                        {"name": "Low",    "color": "red"}
                                    ]}},
                "Reason":           {"rich_text": {}},
                "Effort":           {"select": {"options": [
                                        {"name": "Low"},
                                        {"name": "Medium"},
                                        {"name": "High"}
                                    ]}}
            }
        )
        opportunities_db_id = db["id"]
        print("✅ Opportunities DB created")
    else:
        print("✅ Opportunities DB found")

    return profile_db_id, opportunities_db_id


if __name__ == "__main__":
    profile_id, opps_id = get_or_create_databases()
    print(f"\n🎯 Profile DB ID:       {profile_id}")
    print(f"🎯 Opportunities DB ID: {opps_id}")
    print("\n✅ Setup complete. Add these to your .env file.")