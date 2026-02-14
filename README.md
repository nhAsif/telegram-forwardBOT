# Telegram Auto Forwarder

A simple and efficient Python script to automatically forward messages between Telegram channels or groups using the **Telethon** library.

---

## 🚀 Setup Instructions

### Step 1: Install Dependencies
Ensure you have Python installed, then run the following command to install the required library:
```bash
pip install telethon


Step 2: Get API Credentials
To interact with Telegram's API, you need your own API ID and Hash:
Visit https://my.telegram.org.
Log in with your phone number.
Navigate to API development tools.
Create a new application (you can use any name).
Copy your API ID and API HASH into your script configuration.
Step 3: Run the Script
Once configured, launch the application from your terminal:

Bash


python auto_forwarder.py


🛠 How to Use
Step 4: Get Chat IDs
Before forwarding, you need the unique identifiers for your chats:
Run the script and select option:
1. List chats
Copy the IDs for the source and destination (usually starting with -100).
Step 5: Start Forwarding
To begin the automated process:
Select option:
2. Start auto forward
Provide the IDs when prompted.
Example Configuration
Role
Chat ID
Source Chat ID
-1001234567890
Destination ID
-1009876543210


