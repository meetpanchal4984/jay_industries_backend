import os
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

# Force load .env from the current directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "").replace(" ", "")
CONTACT_RECEIVER = os.getenv("CONTACT_RECEIVER", "meetpanchal5903@gmail.com")

print(f"DEBUG: Using SMTP_USER: {SMTP_USER}")
print(f"DEBUG: Using SMTP_SERVER: {SMTP_SERVER}:{SMTP_PORT}")
print(f"DEBUG: SMTP_PASS is {'set' if SMTP_PASS else 'NOT SET'}")

# FastAPI-Mail Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=SMTP_USER,
    MAIL_PASSWORD=SMTP_PASS,
    MAIL_FROM=SMTP_USER, # Must match your Gmail account
    MAIL_PORT=SMTP_PORT,
    MAIL_SERVER=SMTP_SERVER,
    MAIL_STARTTLS=True if SMTP_PORT == 587 else False,
    MAIL_SSL_TLS=True if SMTP_PORT == 465 else False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_FROM_NAME="Jay Industries"
)

async def send_contact_email(name: str, email: str, phone: str, subject: str, message: str):
    """Send contact inquiry email to admin and confirmation to user."""
    
    # 1. Admin Notification HTML
    admin_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #E86624;">New Contact Inquiry from {name}</h2>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone}</p>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Message:</strong></p>
        <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #E86624;">
            {message}
        </div>
    </body>
    </html>
    """

    # 2. User Confirmation HTML
    user_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eee; padding: 20px;">
            <h2 style="color: #E86624;">Hello {name},</h2>
            <p>Thank you for contacting <strong>Jay Industries</strong>. We have received your message regarding "<strong>{subject}</strong>".</p>
            <p>Our team will review your inquiry and get back to you as soon as possible.</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 12px; color: #777;">This is an automated confirmation. Please do not reply directly to this email.</p>
        </div>
    </body>
    </html>
    """

    fm = FastMail(conf)

    # Send Notification to Admin
    admin_msg = MessageSchema(
        subject=f"URGENT: New Inquiry - {subject}",
        recipients=[CONTACT_RECEIVER],
        body=admin_html,
        subtype=MessageType.html,
        reply_to=[email]
    )

    # Send Confirmation to User
    user_msg = MessageSchema(
        subject="We've received your message - Jay Industries",
        recipients=[email],
        body=user_html,
        subtype=MessageType.html
    )

    try:
        # Send both emails
        await fm.send_message(admin_msg)
        print(f"[SUCCESS] Admin notification sent to {CONTACT_RECEIVER}")
        
        await fm.send_message(user_msg)
        print(f"[SUCCESS] Confirmation sent to user: {email}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Email sending failed: {e}")
        return False
