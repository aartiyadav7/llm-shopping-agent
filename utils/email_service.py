import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL_SERVICE = os.getenv("EMAIL_SERVICE", "RESEND")
API_KEY = os.getenv("EMAIL_SERVICE_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")

# ✅ Use sandbox API for local testing
RESEND_API_URL = "https://api.resend.com/emails"


# ----------------------------------------------------------
# 📨 1. Welcome Email
# ----------------------------------------------------------
def send_welcome_email(to_email: str):
    if not API_KEY:
        print("❌ Email API key missing. Check .env configuration.")
        return False

    subject = "🎉 Welcome to AI Shopping Agent!"
    message_html = f"""
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color:#667eea;">Welcome to AI Shopping Agent!</h2>
        <p>Hi there 👋,</p>
        <p>Thanks for subscribing! We're thrilled to have you onboard.</p>
        <p>Here's your <strong style="color:#764ba2;">10% OFF</strong> coupon code:
           <span style="background:#edf2ff; padding:6px 10px; border-radius:5px; font-weight:bold;">WELCOME10</span></p>
        <p>Use it at checkout on your next purchase.</p>
        <br>
        <p>Happy Shopping,<br><strong>The AI Shopping Agent Team</strong></p>
    </div>
    """

    try:
        response = requests.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": f"AI Shopping Agent <{SENDER_EMAIL}>",
                "to": [to_email],
                "subject": subject,
                "html": message_html,
            },
        )

        if response.status_code in [200, 201, 202]:
            print(f"✅ Welcome email sent successfully to {to_email}")
            return True
        else:
            print(f"⚠️ Email sending failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False


# ----------------------------------------------------------
# 🛒 2. Cart Abandonment Reminder
# ----------------------------------------------------------
def send_cart_abandonment_email(to_email: str, cart_items: list):
    if not API_KEY:
        return False

    items_html = "".join([
        f"<li>{item['name']} - <strong>${item['price']:.2f}</strong></li>"
        for item in cart_items[:5]
    ])

    subject = "🛍️ Your cart misses you!"
    message_html = f"""
    <div style="font-family: Arial, sans-serif;">
        <h2 style="color:#764ba2;">You left something behind 👀</h2>
        <p>You left these items in your cart:</p>
        <ul>{items_html}</ul>
        <a href="http://localhost:8501" 
           style="background-color:#667eea; color:white; padding:10px 20px; text-decoration:none;
                  border-radius:5px; display:inline-block; margin-top:10px;">
            Complete Your Purchase
        </a>
    </div>
    """

    try:
        response = requests.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": f"AI Shopping Agent <{SENDER_EMAIL}>",
                "to": [to_email],
                "subject": subject,
                "html": message_html,
            },
        )
        return response.status_code in [200, 201, 202]
    except Exception as e:
        print(f"❌ Error sending cart email: {str(e)}")
        return False


# ----------------------------------------------------------
# 💰 3. Price Drop Notification
# ----------------------------------------------------------
def send_price_drop_alert(to_email: str, product_name: str, old_price: float, new_price: float):
    if not API_KEY:
        return False

    savings = old_price - new_price
    subject = f"💰 Price Drop Alert: {product_name}"

    message_html = f"""
    <div style="font-family: Arial, sans-serif;">
        <h2 style="color:#51cf66;">Great News! Price Drop Alert 📉</h2>
        <p>The price of <strong>{product_name}</strong> just dropped!</p>
        <p style="font-size: 1.2rem;">
            <span style="text-decoration: line-through; color: #999;">${old_price:.2f}</span>
            <span style="color: #51cf66; font-weight: bold;"> ${new_price:.2f}</span>
        </p>
        <p>You save <strong style="color: #ff6b6b;">${savings:.2f}</strong>!</p>
        <a href="http://localhost:8501"
           style="background-color:#51cf66; color:white; padding:10px 20px;
                  text-decoration:none; border-radius:5px; display:inline-block;">
           Shop Now
        </a>
    </div>
    """

    try:
        response = requests.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": f"AI Shopping Agent <{SENDER_EMAIL}>",
                "to": [to_email],
                "subject": subject,
                "html": message_html,
            },
        )
        return response.status_code in [200, 201, 202]
    except Exception as e:
        print(f"❌ Error sending price drop alert: {str(e)}")
        return False
