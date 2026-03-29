from mcp.server.fastmcp import FastMCP

from core.profile_loader import load_profile
from core.email_source import fetch_emails
from core.extractor import extract_all
from agent import build_prompt
import json, os
from groq import Groq
from notion_client import Client
print("🚀 MCP Server starting...")
mcp = FastMCP("OpportunityAgent")

client = Groq(api_key=os.environ["GROQ_API_KEY"])
notion = Client(auth=os.environ["NOTION_API_KEY"])
DB_ID = os.environ["OPPORTUNITIES_DB_ID"]
@mcp.tool()
def get_opportunities():
    profile = load_profile()
    emails = fetch_emails()
    opportunities = extract_all(emails)

    return {
        "profile": profile,
        "opportunities": opportunities
    }
@mcp.tool()
def decide(profile: dict, opportunities: list):
    prompt = build_prompt(profile, opportunities)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)

@mcp.tool()
def write_results(decisions: list):
    for d in decisions:
        notion.pages.create(
            parent={"database_id": DB_ID},
            properties={
                "Name": {"title": [{"text": {"content": d["title"]}}]},
                "Priority": {"select": {"name": d["priority"]}},
                "Action": {"select": {"name": d["action"]}},
            }
        )
    return "Done"

if __name__ == "__main__":
    mode = input("Mode (test/server): ")

    if mode == "test":
        print("🧪 Running MCP test...")

        ctx = get_opportunities()
        decisions = decide(ctx["profile"], ctx["opportunities"])

        for d in decisions:
            print(f"{d['title']} → {d['action']} ({d['priority']})")

        write_results(decisions)
        print("✅ Test complete")

    else:
        print("🚀 MCP Server running...")
        mcp.run()