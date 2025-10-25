"""
Email Service using SendGrid
More reliable than Resend, works with any email
Uses requests library to bypass SSL issues on university networks
"""

import os
import requests
from typing import Optional

# Initialize SendGrid
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "onepromptsx@gmail.com")

if SENDGRID_API_KEY:
    print(f"SendGrid initialized with from email: {FROM_EMAIL}")
else:
    print("WARNING: SENDGRID_API_KEY not set, emails will print to console")


def send_email_via_api(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send email using SendGrid API with requests library
    Bypasses SSL issues that occur with sendgrid-python on university networks
    """
    if not SENDGRID_API_KEY:
        return False
    
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "personalizations": [{
            "to": [{"email": to_email}]
        }],
        "from": {"email": FROM_EMAIL},
        "subject": subject,
        "content": [{
            "type": "text/html",
            "value": html_content
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 202:
            print(f"Email sent successfully to {to_email} (Status: {response.status_code})")
            return True
        else:
            print(f"SendGrid API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


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
    if not SENDGRID_API_KEY:
        print(f"\n{'='*60}")
        print(f"FALLBACK OTP for {to_email}: {otp}")
        print(f"{'='*60}\n")
        return False
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
                font-size: 36px;
                font-weight: bold;
                letter-spacing: 8px;
                background: white;
                color: #667eea;
                padding: 20px;
                border-radius: 8px;
                margin: 30px 0;
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
            <p>This code will expire in 10 minutes.</p>
            <div class="footer">
                <p>If you didn't request this, please ignore this email.</p>
                <p>OPS-X - Build Startups in One Prompt</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    result = send_email_via_api(
        to_email=to_email,
        subject=f"Your OPS-X Verification Code: {otp}",
        html_content=html_content
    )
    
    if not result:
        print(f"\n{'='*60}")
        print(f"FALLBACK OTP for {to_email}: {otp}")
        print(f"{'='*60}\n")
    
    return result


def send_team_invite_email(
    to_email: str,
    inviter_name: str,
    project_name: str,
    otp: str,
    role: str,
    project_id: int,
    stakeholder_id: int,
    invite_url: str = "http://localhost:3000"
) -> bool:
    """
    Send team invitation email with OTP
    
    Args:
        to_email: Recipient email
        inviter_name: Name of person sending invite
        project_name: Name of the project
        otp: 6-digit OTP code
        role: Team member role
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not SENDGRID_API_KEY:
        join_link = f"{invite_url}/join?code={otp}&project={project_id}&stakeholder={stakeholder_id}"
        print(f"\n{'='*60}")
        print(f"TEAM INVITE OTP for {to_email}: {otp}")
        print(f"Project: {project_name} | Role: {role}")
        print(f"Join Link: {join_link}")
        print(f"{'='*60}\n")
        return False
    
    # Build the invite link
    join_link = f"{invite_url}/join?code={otp}&project={project_id}&stakeholder={stakeholder_id}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 16px;
                padding: 48px 32px;
                text-align: center;
                color: white;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            .role-badge {{
                display: inline-block;
                background: rgba(255,255,255,0.25);
                color: white;
                padding: 10px 24px;
                border-radius: 24px;
                font-weight: 600;
                font-size: 16px;
                margin: 16px 0;
                backdrop-filter: blur(10px);
            }}
            .join-button {{
                display: inline-block;
                background: white;
                color: #667eea;
                padding: 18px 48px;
                border-radius: 12px;
                text-decoration: none;
                font-weight: 700;
                font-size: 18px;
                margin: 32px 0 16px 0;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                transition: transform 0.2s;
            }}
            .join-button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 12px 24px rgba(0,0,0,0.3);
            }}
            .backup-code {{
                font-size: 14px;
                margin-top: 24px;
                padding: 16px;
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
                backdrop-filter: blur(10px);
            }}
            .code-value {{
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 4px;
                margin: 8px 0;
                color: #ffd700;
            }}
            .footer {{
                margin-top: 32px;
                font-size: 14px;
                opacity: 0.9;
                line-height: 1.8;
            }}
            h1 {{
                font-size: 36px;
                margin: 0 0 16px 0;
                font-weight: 800;
            }}
            h2 {{
                font-size: 28px;
                margin: 8px 0 16px 0;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 You're Invited!</h1>
            <p style="font-size: 18px;"><strong>{inviter_name}</strong> invited you to join:</p>
            <h2>{project_name}</h2>
            <div class="role-badge">🎯 {role}</div>
            
            <div style="margin: 40px 0;">
                <a href="{join_link}" class="join-button">
                    Accept Invitation & Join Team
                </a>
            </div>
            
            <div class="backup-code">
                <p style="margin: 0; font-size: 13px;">Or use this code manually:</p>
                <div class="code-value">{otp}</div>
                <p style="margin: 8px 0 0 0; font-size: 12px; opacity: 0.8;">Expires in 30 minutes</p>
            </div>
            
            <div class="footer">
                <p>Click the button above to create your account and join the team!</p>
                <p style="margin: 8px 0;">⚡ OPS-X - Build Startups in One Prompt</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    result = send_email_via_api(
        to_email=to_email,
        subject=f"Join {project_name} on OPS-X as {role}",
        html_content=html_content
    )
    
    if not result:
        print(f"\n{'='*60}")
        print(f"TEAM INVITE OTP for {to_email}: {otp}")
        print(f"Project: {project_name} | Role: {role}")
        print(f"{'='*60}\n")
    
    return result
