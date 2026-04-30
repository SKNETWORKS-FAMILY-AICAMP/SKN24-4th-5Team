import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_email(receiver_email):
    EMAIL_ADDRESS = "visalavista.biz@gmail.com"
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    msg = EmailMessage()
    msg['Subject'] = "Status Update: 2026 Project"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = receiver_email
    
    # fallback
    msg.set_content("Hello! This is a secure email sent from Python 3.12.")

    # HTML 
    html_content = """
    <html>
        <body>
            <h1 style="color: SlateBlue;">Automated Report</h1>
            <p>The Python script executed <b>successfully</b>.</p>
        </body>
    </html>
    """
    msg.add_alternative(html_content, subtype='html')

    try:
        # SSL (Port 465) for Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"{receiver_email} 로 이메일 전송 성공!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_email("hahahafunnydude@gmail.com")