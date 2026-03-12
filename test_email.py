import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("EMAIL_SERVICE_KEY")
SENDER = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")
TO_EMAIL = "your_email@gmail.com"

print("Using API key:", API_KEY[:10], "...")

try:
    r = requests.post(
        "https://api.resend.com/emails",  # ✅ switch from .dev to .com
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": f"AI Shopping Agent <{SENDER}>",
            "to": [TO_EMAIL],
            "subject": "✅ Test Email from AI Shopping Agent",
            "html": "<strong>This is a test email — setup works!</strong>",
        },
    )

    if r.status_code in [200, 201, 202]:
        print("✅ Email sent successfully!")
    else:
        print(f"❌ Email failed: {r.status_code} - {r.text}")

except Exception as e:
    print("❌ Error sending email:", e)
