# extractor.py
import re

def extract_opportunity(email):
    """Converts raw email → structured opportunity dict."""
    
    subject = email.get("subject", "").lower()
    body    = email.get("body", "").lower()
    text    = subject + " " + body

    # --- Type Detection ---
    if any(w in text for w in ["intern", "job", "role", "position", "hiring"]):
        opp_type = "Job"
    elif any(w in text for w in ["hackathon", "hack", "build", "challenge"]):
        opp_type = "Hackathon"
    elif any(w in text for w in ["oa", "online assessment", "assessment", "test"]):
        opp_type = "OA"
    else:
        opp_type = "Other"

    # --- Skill Extraction ---
    skill_keywords = [
        "python", "java", "javascript", "react", "sql", "dsa",
        "machine learning", "ml", "pytorch", "tensorflow", "pandas",
        "spring boot", "git", "dbms", "c++", "computer vision",
        "data science", "nlp", "docker", "kubernetes", "node"
    ]
    found_skills = [s for s in skill_keywords if s in text]

    # --- Deadline Extraction ---
    deadline_days = 7  # default
    match = re.search(r'(\d+)\s*day', text)
    if match:
        deadline_days = int(match.group(1))
    elif "no hard deadline" in text or "no deadline" in text:
        deadline_days = 30

    # --- Effort Estimation ---
    if opp_type == "Hackathon":
        effort = "High"
    elif opp_type == "OA":
        effort = "Medium"
    elif deadline_days <= 2:
        effort = "Medium"
    else:
        effort = "Low"

    return {
        "id":            email["id"],
        "title":         email["subject"],
        "type":          opp_type,
        "skills":        found_skills,
        "deadline_days": deadline_days,
        "effort":        effort,
        "raw_body":      email["body"]
    }


def extract_all(emails):
    return [extract_opportunity(e) for e in emails]


if __name__ == "__main__":
    from core.email_source import fetch_emails
    emails = fetch_emails()
    opportunities = extract_all(emails)
    
    print(f"\n📬 Extracted {len(opportunities)} opportunities:\n")
    for opp in opportunities:
        print(f"  [{opp['type']}] {opp['title']}")
        print(f"    Skills:   {opp['skills']}")
        print(f"    Deadline: {opp['deadline_days']} days")
        print(f"    Effort:   {opp['effort']}")
        print()