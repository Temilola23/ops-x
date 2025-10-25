"""
Email Service using Resend
Free tier: 3,000 emails/month, 100 emails/day
"""

import os
import resend
from typing import Optional

# Initialize Resend
resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "OPS-X <onboarding@resend.dev>")


def send_otp_email(to_email: str, otp: str, name: str) -> bool:
    """
    Send OTP email to user
    
    Args:
        to_email: Recipient email
        otp: 6-digit OTP code
        name: User's name
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        if not resend.api_key:
            print("WARNING: RESEND_API_KEY not set, email not sent")
            print(f"OTP for {to_email}: {otp}")
            return False
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px;
                    padding: 40px;
                    text-align: center;
                    color: white;
                }}
                .otp-code {{
                    background: white;
                    color: #667eea;
                    font-size: 36px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 30px 0;
                    display: inline-block;
                }}
                .footer {{
                    margin-top: 30px;
                    font-size: 14px;
                    opacity: 0.9;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to OPS-X!</h1>
                <p>Hi {name},</p>
                <p>Your verification code is:</p>
                <div class="otp-code">{otp}</div>
                <p>This code will expire in <strong>10 minutes</strong>.</p>
                <p>If you didn't request this code, please ignore this email.</p>
                <div class="footer">
                    <p>Built for Cal Hacks 12.0</p>
                    <p>One-Prompt Startup Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": f"Your OPS-X Verification Code: {otp}",
            "html": html_content,
        }
        
        email = resend.Emails.send(params)
        print(f"OTP email sent to {to_email} (ID: {email.get('id', 'unknown')})")
        return True
        
    except Exception as e:
        print(f"Failed to send OTP email to {to_email}: {str(e)}")
        # Fallback: print OTP to console for demo
        print(f"FALLBACK OTP for {to_email}: {otp}")
        return False


def send_team_invite_email(to_email: str, inviter_name: str, project_name: str, otp: str, role: str) -> bool:
    """
    Send team invitation email with OTP
    
    Args:
        to_email: Recipient email
        inviter_name: Name of person who invited
        project_name: Name of the project
        otp: 6-digit OTP code
        role: Team member role (Frontend, Backend, etc.)
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        if not resend.api_key:
            print("WARNING: RESEND_API_KEY not set, email not sent")
            print(f"Team Invite OTP for {to_email}: {otp}")
            return False
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    border-radius: 10px;
                    padding: 40px;
                    text-align: center;
                    color: white;
                }}
                .project-info {{
                    background: rgba(255,255,255,0.2);
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .otp-code {{
                    background: white;
                    color: #f5576c;
                    font-size: 36px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 30px 0;
                    display: inline-block;
                }}
                .role-badge {{
                    display: inline-block;
                    background: rgba(255,255,255,0.3);
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>You've Been Invited!</h1>
                <p><strong>{inviter_name}</strong> invited you to join their project:</p>
                <div class="project-info">
                    <h2>{project_name}</h2>
                    <div class="role-badge">{role}</div>
                </div>
                <p>Your verification code to join is:</p>
                <div class="otp-code">{otp}</div>
                <p>This code will expire in <strong>30 minutes</strong>.</p>
                <p>Enter this code when signing up to join the team!</p>
            </div>
        </body>
        </html>
        """
        
        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": f"You're invited to join {project_name} on OPS-X!",
            "html": html_content,
        }
        
        email = resend.Emails.send(params)
        print(f"Team invite email sent to {to_email} (ID: {email.get('id', 'unknown')})")
        return True
        
    except Exception as e:
        print(f"Failed to send team invite to {to_email}: {str(e)}")
        # Fallback: print OTP to console
        print(f"FALLBACK Team Invite OTP for {to_email}: {otp}")
        return False


# Test function
if __name__ == "__main__":
    print("Testing email service...")
    print(f"RESEND_API_KEY configured: {bool(resend.api_key)}")
    
    # Test OTP email
    send_otp_email("test@example.com", "123456", "Test User")
    
    # Test team invite
    send_team_invite_email(
        "team@example.com",
        "John Doe",
        "My Awesome Project",
        "654321",
        "Frontend Engineer"
    )

