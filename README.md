# 🎯 Opportunity Decision Agent

> An AI-powered agent that reads your Gmail, evaluates career opportunities against your student profile, and pushes prioritized decisions directly into a Notion database — all via a custom MCP server.

**Built for the [Notion MCP Challenge](https://dev.to/challenges/notion-2026-03-04) in partnership with MLH & DEV.**

---

## 🧠 What It Does

Students get overwhelmed by a flood of internship emails, hackathon invites, scholarship deadlines, and job postings. This agent cuts through the noise:

1. **Fetches** recent emails from Gmail (or mock data for demo)
2. **Extracts** structured opportunity data — title, type, required skills, deadline, effort level
3. **Loads** your personal student profile from a Notion database (target role, skills, available hours, career phase)
4. **Reasons** over each opportunity using Llama 3.3 70B via Groq — scoring role alignment, skill gaps, deadline urgency, effort vs. availability, and long-term career value
5. **Writes** the full ranked decision set back to your Notion Opportunities database with action (`Apply / Prepare / Consider / Skip`), priority, confidence, and plain-English reasoning

The result: you open Notion every morning and know exactly what to act on.

---

## 🏗️ Architecture

```
Gmail API (or mock_emails.py)
        │
        ▼
core/email_source.py      ← Fetches raw emails
        │
        ▼
core/extractor.py         ← Parses into structured opportunity objects
        │
        ▼
core/profile_loader.py    ← Reads your profile from Notion (creates it on first run)
        │
        ▼
agent.py                  ← Builds prompt → Groq (Llama 3.3 70B) → parses JSON decisions
        │
        ▼
Notion API                ← Writes/refreshes your Opportunities database
```

The project also exposes an **MCP server** (`mcp_server.py`) with three tools:
- `get_opportunities` — fetches and extracts email opportunities
- `decide` — runs LLM reasoning on a profile + opportunity set
- `write_results` — pushes decisions into Notion

This lets any MCP-compatible AI client (Claude Desktop, etc.) orchestrate the full pipeline conversationally.

---

## 📁 Project Structure

```
opportunity-decision-agent/
├── agent.py                  # Standalone runner (full end-to-end pipeline)
├── mcp_server.py             # FastMCP server exposing tools for AI clients
├── requirements.txt
├── .gitignore
├── core/
│   ├── email_source.py       # Gmail fetching (or mock fallback)
│   ├── mock_emails.py        # Sample emails for demo/testing
│   ├── extractor.py          # Opportunity extraction from email text
│   └── profile_loader.py     # Reads/creates student profile in Notion
└── setup/
    ├── notion_setup.py       # Auto-creates both Notion DBs on first run
    ├── fix_opportunities_db.py
    └── fix_profile_db.py
```

---

## ⚙️ Setup

### Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com/) (free tier works)
- A [Notion integration token](https://www.notion.so/my-integrations) with access to your workspace
- Gmail API credentials (optional — mock emails work out of the box)

---

### 1. Clone & install

```bash
git clone https://github.com/Sarah4908/opportunity-decision-agent.git
cd opportunity-decision-agent
pip install -r requirements.txt
```

---

### 2. Create a Notion integration

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) and create a new integration
2. Copy the **Internal Integration Token**
3. In your Notion workspace, create a blank page (e.g. "Agent Dashboard") and share it with your integration via the **"..."** menu → Connections

---

### 3. Set up environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
NOTION_API_KEY=your_notion_integration_token
NOTION_PARENT_PAGE_ID=your_parent_page_id
OPPORTUNITIES_DB_ID=        # filled in after step 4
PROFILE_DB_ID=              # filled in after step 4
```

To get `NOTION_PARENT_PAGE_ID`: open the page you shared with the integration in Notion, copy the URL — the ID is the 32-character string at the end.

---

### 4. Auto-create Notion databases

```bash
python setup/notion_setup.py
```

This will:
- Search your workspace for existing `User Profile` and `Opportunities` databases
- Create them under your parent page if they don't exist
- Print both database IDs

Copy the printed IDs into your `.env`:

```env
OPPORTUNITIES_DB_ID=paste_id_here
PROFILE_DB_ID=paste_id_here
```

---

### 5. Run the agent

```bash
python agent.py
```

On **first run**, you'll be prompted to fill in your student profile (target role, skills, hours/week, career phase). This gets saved to your Notion Profile database and never asked again.

On every subsequent run, it goes straight to fetching → reasoning → updating Notion.

---

### Gmail setup (optional)

By default the agent runs on mock emails. To connect real Gmail:

1. Enable the Gmail API in [Google Cloud Console](https://console.cloud.google.com/)
2. Download `credentials.json` and place it in the project root
3. In `core/email_source.py`, flip:

```python
USE_REAL_GMAIL = True
```

A browser window will open for OAuth on first run. A `token.json` will be saved for subsequent runs.

---

## 🚀 Running Modes

### Standalone (recommended for first run)

```bash
python agent.py
```

### MCP server (for Claude Desktop or other MCP clients)

```bash
python mcp_server.py
# Enter "server" when prompted
```

Quick local test without a client:

```bash
python mcp_server.py
# Enter "test" when prompted
```

> ⚠️ Make sure you've run `python agent.py` at least once to set up your profile before starting the MCP server. The server doesn't support the interactive profile onboarding prompt.

### Connecting to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "opportunity-agent": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server.py"],
      "env": {
        "GROQ_API_KEY": "...",
        "NOTION_API_KEY": "...",
        "OPPORTUNITIES_DB_ID": "...",
        "PROFILE_DB_ID": "..."
      }
    }
  }
}
```

Then in Claude Desktop: *"Check my latest opportunities and update my Notion dashboard."*

---

## 🔍 How Notion MCP Is Used

Notion is the **central hub** of this entire workflow — not just an output sink:

- **Profile database** — your student profile lives in Notion. `profile_loader.py` reads it on every run. On first run it creates it interactively and saves it there permanently.
- **Opportunities database** — every run clears and rewrites the full decision set so your dashboard always reflects the latest reasoning.
- **MCP server** — `mcp_server.py` exposes the pipeline as callable tools, meaning any MCP-compatible AI client can trigger the full workflow (fetch → reason → write to Notion) in a single conversation turn.

Notion becomes the persistent, human-readable output of an otherwise fully automated agentic loop. The "human-in-the-loop" moment is simply opening your dashboard.

---

## 📊 Example Output

**Terminal:**
```
🚀 Opportunity Agent Starting...
✅ Profile loaded: ML Engineer | Intern Hunting
📬 Found 5 opportunities

🧠 Sending to LLM for reasoning...
📊 Writing decisions to Notion...

  ✅ Written: Amazon OA Invitation → Apply (High priority)
  ✅ Written: Data Science Intern - StartupABC → Apply (High priority)
  ✅ Written: ML Hackathon 2026 → Prepare (Medium priority)
  ✅ Written: Backend Intern at XYZ Corp → Consider (Low priority)
  ✅ Written: Open Source Contribution → Consider (Low priority)

============================================================
🎯 TOP ACTIONS TODAY:
============================================================

1. Amazon OA Invitation - SDE Intern
   Action: Apply
   Priority: High
   Reason: DSA and Python match your profile; tight 5-day deadline makes this urgent.

2. Data Science Intern - StartupABC
   Action: Apply
   Priority: High
   Reason: Strong skill overlap with Python, Pandas, SQL and ML; deadline in 3 days.
```

**Notion view:** Each opportunity appears as a filterable, sortable row with action, priority, confidence, effort, and plain-English reasoning.

---

## 🧩 Tech Stack

| Layer | Technology |
|---|---|
| LLM reasoning | Llama 3.3 70B via Groq |
| Email source | Gmail API / mock fallback |
| Profile + output | Notion API |
| MCP integration | FastMCP (`mcp` package) |
| Environment | Python 3.10+, python-dotenv |

---

## ⚠️ Known Limitations

- Opportunities database is fully cleared and rewritten on each run — no deduplication yet
- Email extraction uses heuristic keyword matching; complex HTML emails may not parse cleanly
- MCP server mode requires profile to be set up in advance via `agent.py`
- Gmail integration requires Google Cloud Console setup; mock emails are used by default

---

## 📄 License

MIT — fork, adapt, and build on top of this freely.

---

## 🙌 Acknowledgements

- [Notion MCP Documentation](https://developers.notion.com/docs/mcp)
- [Groq](https://groq.com/) — fast LLM inference
- [FastMCP](https://github.com/jlowin/fastmcp) — MCP server framework for Python
- MLH & Notion for running the challenge 🎉
