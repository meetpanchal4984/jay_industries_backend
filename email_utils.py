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

def send_contact_email(name, email, phone, subject, message):
    if not SMTP_USER or not SMTP_PASS:
        print("SMTP credentials not configured. Email not sent.")
        print(f"SMTP_USER: {SMTP_USER}")
        print(f"SMTP_PASS: {'*' * len(SMTP_PASS) if SMTP_PASS else 'Not set'}")
        return False

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER  # Use SMTP_USER instead of email
    msg['To'] = CONTACT_RECEIVER
    msg['Reply-To'] = email
    msg['Subject'] = f"New Contact Inquiry: {subject}"

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
    
    msg.attach(MIMEText(html_content, 'html'))

    try:
        print(f"Attempting to send email to {CONTACT_RECEIVER}")
        print(f"From: {SMTP_USER}")
        print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        
        print(f"✓ Email sent successfully to {CONTACT_RECEIVER}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print(f"Check your Gmail app password. Make sure you're using an App Password, not your regular Gmail password.")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        import traceback
        traceback.print_exc()
        return False
