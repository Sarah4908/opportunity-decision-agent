# agent.py
import os
import json
from groq import Groq
from notion_client import Client
from dotenv import load_dotenv
from core.email_source import fetch_emails
from core.extractor import extract_all
from core.profile_loader import load_profile

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])
notion = Client(auth=os.environ["NOTION_API_KEY"])
OPPORTUNITIES_DB_ID = os.environ["OPPORTUNITIES_DB_ID"]

def build_prompt(profile, opportunities):
    opp_text = ""
    for i, opp in enumerate(opportunities, 1):
        opp_text += f"""
Opportunity {i}:
- Title: {opp['title']}
- Type: {opp['type']}
- Skills Required: {', '.join(opp['skills']) if opp['skills'] else 'Not specified'}
- Deadline: {opp['deadline_days']} days
- Effort: {opp['effort']}
"""

    return f"""
You are an AI opportunity decision agent for a student.

STUDENT PROFILE:
- Target Role: {profile['target_role']}
- Current Skills: {', '.join(profile['skills'])}
- Available Hours/Week: {profile['available_hours']}
- Phase: {profile['phase']}

OPPORTUNITIES FROM GMAIL:
{opp_text}

For each opportunity, evaluate based on:
1. Role alignment with target role
2. Skill match and gap 
3. Deadline urgency
4. Effort vs available time
5. Long term career value

Respond ONLY with a valid JSON array. No explanation, no markdown, no backticks.
Each object must have exactly these fields:
- title (string)
- type (string)
- skills (array of strings)
- deadline_days (number)
- effort (string: Low/Medium/High)
- action (string: Apply/Prepare/Consider/Skip)
- priority (string: High/Medium/Low)
- confidence (string: High/Medium/Low)
- reason (string, plain English, 1-2 sentences)

Example format:
[{{"title":"example","type":"Job","skills":["python"],"deadline_days":3,"effort":"Low","action":"Apply","priority":"High","confidence":"High","reason":"Strong match with target role and existing skills."}}]
"""


def write_to_notion(decisions):
    """Writes all decisions to Notion Opportunities database."""
    
    # Clear existing entries first
    existing = notion.databases.query(database_id=OPPORTUNITIES_DB_ID).get("results", [])
    for page in existing:
        notion.pages.update(page_id=page["id"], archived=True)

    for d in decisions:
        notion.pages.create(
            parent={"database_id": OPPORTUNITIES_DB_ID},
            properties={
                "Name": {"title": [{"text": {"content": d["title"]}}]},
                "Type":            {"select": {"name": d["type"]}},
                "Skills Required": {"multi_select": [{"name": s} for s in d["skills"]]},
                "Deadline Days":   {"number": d["deadline_days"]},
                "Priority":        {"select": {"name": d["priority"]}},
                "Action":          {"select": {"name": d["action"]}},
                "Confidence":      {"select": {"name": d["confidence"]}},
                "Reason":          {"rich_text": [{"text": {"content": d["reason"]}}]},
                "Effort":          {"select": {"name": d["effort"]}}
            }
        )
        print(f"  ✅ Written: {d['title']} → {d['action']} ({d['priority']} priority)")


def print_summary(decisions):
    top = [d for d in decisions if d["priority"] == "High"]
    
    print("\n" + "="*60)
    print("🎯 TOP ACTIONS TODAY:")
    print("="*60)
    
    if not top:
        top = decisions[:2]
    
    for i, d in enumerate(top, 1):
        print(f"\n{i}. {d['title']}")
        print(f"   Action:   {d['action']}")
        print(f"   Priority: {d['priority']}")
        print(f"   Reason:   {d['reason']}")
    
    print("\n" + "="*60)
    print("📋 ALL DECISIONS:")
    print("="*60)
    for d in decisions:
        print(f"  [{d['action']:8}] {d['title'][:45]:45} | {d['priority']:6} | {d['confidence']} confidence")


def run():
    print("🚀 Opportunity Agent Starting...\n")
    
    # Step 1 — Load profile
    profile = load_profile()
    
    # Step 2 — Fetch and extract emails
    emails = fetch_emails()
    opportunities = extract_all(emails)
    print(f"📬 Found {len(opportunities)} opportunities\n")
    
    # Step 3 — Send to Gemini for reasoning
    print("🧠 Sending to Gemini for reasoning...\n")
    prompt = build_prompt(profile, opportunities)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
        
    # Step 4 — Parse response
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    decisions = json.loads(raw)
    
    # Step 5 — Write to Notion
    print("📊 Writing decisions to Notion...\n")
    write_to_notion(decisions)
    
    # Step 6 — Print summary
    print_summary(decisions)
    
    print("\n✅ Done. Check your Notion dashboard for full results.")


if __name__ == "__main__":
    run()