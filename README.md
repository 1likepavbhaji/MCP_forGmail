# MCP_forGmail
📧 Gmail MCP Server (Python)

A lightweight Model Context Protocol (MCP) server built in Python that integrates with Gmail API to:

📥 Read emails
🧾 Summarize emails
📤 Send emails
👤 Fetch profile overview

Designed to be used with LLM clients like Claude for natural language interaction with your inbox.

🚀 Features
Gmail Authentication (OAuth2)
Read latest 10 emails
Extract subject, sender, body, date
Send emails programmatically
Summarize emails
Profile overview (total emails, unread count)

🛠️ Tech Stack
Python
MCP (FastMCP)
Gmail API
OAuth 2.0

🧠 Available MCP Tools
1. Profile Overview
prof_overview()

Returns:
Email address
Total messages
Total threads
Unread count

2. Read Emails
read_mail()
Fetches latest 10 inbox emails
Returns:
Sender
Subject
Body
Date

4. Send Email
write_and_send_mail(send_email, send_subject, send_message)

Example:
write_and_send_mail(
    "example@gmail.com",
    "Test Subject",
    "Hello from MCP server!"
)

4. Summarize Emails
summarize_mail()
Combines subject + body
Returns simple text summaries for each email

🔐 Permissions Used
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]
