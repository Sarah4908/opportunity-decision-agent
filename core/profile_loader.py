# profile_loader.py
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.environ["NOTION_API_KEY"])
PROFILE_DB_ID = os.environ["PROFILE_DB_ID"]

def load_profile():
    """Reads profile from Notion. If empty, asks user to fill it once."""
    
    results = notion.databases.query(database_id=PROFILE_DB_ID).get("results", [])
    
    if results:
        # Profile exists — read it
        props = results[0]["properties"]
        
        def get_text(prop):
            items = props.get(prop, {}).get("rich_text", [])
            return items[0]["plain_text"] if items else ""
        
        def get_select(prop):
            sel = props.get(prop, {}).get("select")
            return sel["name"] if sel else ""
        
        def get_multiselect(prop):
            items = props.get(prop, {}).get("multi_select", [])
            return [i["name"] for i in items]
        
        def get_number(prop):
            return props.get(prop, {}).get("number", 0)

        profile = {
            "target_role":      get_text("Target Role"),
            "skills":           get_multiselect("Skills"),
            "available_hours":  get_number("Available Hours"),
            "phase":            get_select("Phase")
        }
        
        print(f"✅ Profile loaded: {profile['target_role']} | {profile['phase']}")
        return profile
    
    else:
        # No profile found — ask user once
        print("\n👤 No profile found. Let's set you up (one time only):\n")
        
        target_role     = input("What is your target role? (e.g. Backend SWE, ML Engineer): ").strip()
        skills_input    = input("What are your current skills? (comma separated, e.g. Python, Java, Git): ").strip()
        hours           = input("How many hours/week can you dedicate? (e.g. 8): ").strip()
        print("Choose your phase:")
        print("  1. Intern Hunting")
        print("  2. Placement Prep")
        print("  3. Learning")
        phase_choice    = input("Enter 1, 2 or 3: ").strip()
        
        phase_map = {"1": "Intern Hunting", "2": "Placement Prep", "3": "Learning"}
        phase = phase_map.get(phase_choice, "Intern Hunting")
        
        skills = [s.strip() for s in skills_input.split(",")]
        
        # Save to Notion
        notion.pages.create(
            parent={"database_id": PROFILE_DB_ID},
            properties={
                "Name":             {"title": [{"text": {"content": target_role}}]},
                "Target Role":      {"rich_text": [{"text": {"content": target_role}}]},
                "Skills":           {"multi_select": [{"name": s} for s in skills]},
                "Available Hours":  {"number": int(hours)},
                "Phase":            {"select": {"name": phase}}
            }
        )
        
        print("\n✅ Profile saved to Notion. Won't ask again.\n")
        
        return {
            "target_role":      target_role,
            "skills":           skills,
            "available_hours":  int(hours),
            "phase":            phase
        }


if __name__ == "__main__":
    profile = load_profile()
    print("\n📋 Your Profile:")
    print(f"  Target Role:     {profile['target_role']}")
    print(f"  Skills:          {', '.join(profile['skills'])}")
    print(f"  Available Hours: {profile['available_hours']}/week")
    print(f"  Phase:           {profile['phase']}")