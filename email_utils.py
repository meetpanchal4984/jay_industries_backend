import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "").replace(" ", "")  # Remove spaces from app password
CONTACT_RECEIVER = os.getenv("CONTACT_RECEIVER", "meetpanchal4984@gmail.com")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@jayindustries.com")

def send_with_sendgrid(name, email, phone, subject, message, html_content):
    """Attempt to send email via SendGrid API."""
    if not SENDGRID_API_KEY or "your_sendgrid_api_key_here" in SENDGRID_API_KEY:
        print("SendGrid API key not configured or still using placeholder.")
        return False
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        print(f"Attempting to send email via SendGrid API to {CONTACT_RECEIVER}")
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        from_email = Email(SENDGRID_FROM_EMAIL)
        to_email = To(CONTACT_RECEIVER)
        mail_subject = f"New Contact Inquiry: {subject}"
        content = Content("text/html", html_content)
        
        mail = Mail(from_email, to_email, mail_subject, content)
        mail.reply_to = Email(email)
        
        response = sg.client.mail.send.post(request_body=mail.get())
        if response.status_code >= 200 and response.status_code < 300:
            print(f"[SUCCESS] Email sent successfully via SendGrid to {CONTACT_RECEIVER}")
            return True
        else:
            print(f"[ERROR] SendGrid error: Status {response.status_code}")
            print(f"Response Body: {response.body}")
            return False
    except ImportError:
        print("[ERROR] SendGrid library not installed. Please add 'sendgrid' to requirements.txt")
        return False
    except Exception as e:
        print(f"[ERROR] SendGrid exception: {e}")
        return False

def send_contact_email(name, email, phone, subject, message):
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
        <div style="background-color: #f5f5f5; padding: 40px 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #E86624 0%, #c94f1c 100%); padding: 30px 20px; text-align: center;">
                    <h1 style="margin: 0; color: white; font-size: 28px; font-weight: 600;">New Contact Inquiry</h1>
                    <p style="margin: 8px 0 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">from Jay Industries Contact Form</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px 20px;">
                    <!-- Message from -->
                    <p style="margin: 0 0 8px 0; color: #666; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Message from</p>
                    <h2 style="margin: 0 0 25px 0; color: #111; font-size: 22px; font-weight: 600;">{name}</h2>
                    
                    <!-- Details Grid -->
                    <table style="width: 100%; margin-bottom: 25px; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 12px 0; border-bottom: 1px solid #e8e8e8; width: 80px;">
                                <p style="margin: 0; color: #E86624; font-weight: 600; font-size: 13px;">Email:</p>
                            </td>
                            <td style="padding: 12px 0 12px 20px; border-bottom: 1px solid #e8e8e8;">
                                <p style="margin: 0; color: #333; font-size: 14px;"><a href="mailto:{email}" style="color: #0066cc; text-decoration: none;">{email}</a></p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 0; border-bottom: 1px solid #e8e8e8; width: 80px;">
                                <p style="margin: 0; color: #E86624; font-weight: 600; font-size: 13px;">Phone:</p>
                            </td>
                            <td style="padding: 12px 0 12px 20px; border-bottom: 1px solid #e8e8e8;">
                                <p style="margin: 0; color: #333; font-size: 14px;">{phone}</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 0; border-bottom: 1px solid #e8e8e8; width: 80px;">
                                <p style="margin: 0; color: #E86624; font-weight: 600; font-size: 13px;">Subject:</p>
                            </td>
                            <td style="padding: 12px 0 12px 20px; border-bottom: 1px solid #e8e8e8;">
                                <p style="margin: 0; color: #333; font-size: 14px;">{subject}</p>
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Message Box -->
                    <div style="background: linear-gradient(to right, #E86624 0%, #E86624 4px, #f9f9f9 4px, #f9f9f9 100%); padding: 0; border-radius: 4px; margin-top: 20px;">
                        <div style="padding: 20px; background-color: #f9f9f9;">
                            <p style="margin: 0 0 10px 0; color: #E86624; font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">Message</p>
                            <p style="margin: 0; color: #333; font-size: 14px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word;">{message}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f9f9f9; border-top: 1px solid #e8e8e8; padding: 20px; text-align: center;">
                    <p style="margin: 0; color: #999; font-size: 12px; line-height: 1.6;">
                        This message was sent via the Jay Industries contact form.<br>
                        <span style="color: #bbb;">© Jay Industries. All rights reserved.</span>
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Try SendGrid first as it's more reliable on platforms like Render
    if SENDGRID_API_KEY and "your_sendgrid_api_key_here" not in SENDGRID_API_KEY:
        if send_with_sendgrid(name, email, phone, subject, message, html_content):
            return True
        print("SendGrid failed, falling back to SMTP...")

    # Fallback to SMTP (might fail on Render Free Tier)
    if not SMTP_USER or not SMTP_PASS:
        print("SMTP credentials not configured. Email not sent.")
        print(f"SMTP_USER: {SMTP_USER}")
        print(f"SMTP_PASS: {'*' * len(SMTP_PASS) if SMTP_PASS else 'Not set'}")
        return False

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = CONTACT_RECEIVER
    msg['Reply-To'] = email
    msg['Subject'] = f"New Contact Inquiry: {subject}"
    msg.attach(MIMEText(html_content, 'html'))

    try:
        print(f"Attempting to send email via SMTP to {CONTACT_RECEIVER}")
        print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
        
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
            server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        
        print(f"[SUCCESS] Email sent successfully to {CONTACT_RECEIVER}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[ERROR] SMTP Authentication failed: {e}")
        print(f"Check your Gmail app password. Make sure you're using an App Password, not your regular Gmail password.")
        return False
    except OSError as e:
        if "[Errno 101]" in str(e) or "Network is unreachable" in str(e):
            print(f"[ERROR] Network Error: {e}")
            print("This usually happens on Render's Free tier because they block SMTP ports (25, 465, 587).")
            print("ACTION REQUIRED: Please provide a SendGrid API Key in your environment variables to bypass this restriction.")
        else:
            print(f"[ERROR] Network error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error sending email: {e}")
        return False
