# email_source.py
USE_REAL_GMAIL = False  # ← flip to True later

if USE_REAL_GMAIL:
    from gmail_fetcher import fetch_emails
else:
    from data.mock_emails import MOCK_EMAILS
    def fetch_emails():
        return MOCK_EMAILS