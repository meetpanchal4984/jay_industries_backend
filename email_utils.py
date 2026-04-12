import os
import resend
from dotenv import load_dotenv

load_dotenv()

# Apply the user's explicit API Key
resend.api_key = os.getenv("RESEND_API_KEY")

async def send_contact_email(name: str, email: str, phone: str, subject: str, message: str):
    """
    Sends a beautifully structured contact inquiry to the business owner via Resend using the verified domain constraints.
    """
    admin_html = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1f2937; max-width: 600px; margin: 0 auto; line-height: 1.6; background-color: #f9fafb; padding: 20px;">
        <div style="background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); border: 1px solid #f3f4f6;">
            
            <div style="padding: 30px; text-align: center; border-bottom: 3px solid #ea580c;">
                <h1 style="color: #111827; margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">JAY INDUSTRIES</h1>
                <p style="color: #ea580c; font-size: 14px; font-weight: 600; margin: 8px 0 0 0; text-transform: uppercase; letter-spacing: 1px;">New Customer Inquiry</p>
            </div>
            
            <div style="padding: 30px;">
                <p style="margin: 0 0 25px 0; font-size: 16px; color: #4b5563;">You have received a new message from your website's contact form. Please find the details below:</p>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; width: 130px; font-weight: 600; color: #9ca3af; font-size: 13px; text-transform: uppercase;">Full Name</td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; color: #111827; font-weight: 500;">{name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; font-weight: 600; color: #9ca3af; font-size: 13px; text-transform: uppercase;">Email Address</td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6;"><a href="mailto:{email}" style="color: #ea580c; text-decoration: none; font-weight: 500;">{email}</a></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; font-weight: 600; color: #9ca3af; font-size: 13px; text-transform: uppercase;">Phone Number</td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6;"><a href="tel:{phone}" style="color: #111827; text-decoration: none; font-weight: 500;">{phone}</a></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; font-weight: 600; color: #9ca3af; font-size: 13px; text-transform: uppercase;">Subject</td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; color: #111827; font-weight: 500;">{subject}</td>
                    </tr>
                </table>
                
                <h3 style="font-size: 13px; color: #9ca3af; margin: 0 0 10px 0; text-transform: uppercase; font-weight: 600;">Message Content</h3>
                <div style="background: #f9fafb; padding: 20px; border-radius: 8px; font-size: 15px; color: #374151; line-height: 1.6; white-space: pre-wrap; border: 1px solid #f3f4f6;">
{message}
                </div>
                
            </div>
            
            <div style="background: #fdfbf9; text-align: center; font-size: 12px; color: #9ca3af; padding: 20px; border-top: 1px solid #f3f4f6;">
                This message was sent from the Jay Industries website automated system.
            </div>
            
        </div>
    </body>
    </html>
    """

    try:
        r = resend.Emails.send({
            # The 'from' must be onboarding@resend.dev unless a custom domain is verified
            "from": "Jay Industries <onboarding@resend.dev>",
            "to": "bipinjski@gmail.com",
            # We set reply_to as the contact's email so when you hit "Reply", it goes to them
            "reply_to": email,
            "subject": f"New Inquiry: {subject} - {name}",
            "html": admin_html
        })
        print(f"[SUCCESS] Resend executed successfully: {r}")
        return True
    except Exception as e:
        print(f"[ERROR] Resend execution failed: {e}")
        return False
