import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_email(receiver_email, verification_code):
    EMAIL_ADDRESS = "visalavista.biz@gmail.com"
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    if not EMAIL_PASSWORD:
        return False

    msg = EmailMessage()
    msg['Subject'] = "Visa La Vista 이메일 인증번호"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = receiver_email
    
    msg.set_content(f"Visa La Vista 인증번호는 {verification_code} 입니다. 5분 안에 입력해주세요.")

    html_content = """
    <html>
        <body>
            <h1 style="color: #24308f;">Visa La Vista 이메일 인증</h1>
            <p>아래 인증번호를 5분 안에 입력해주세요.</p>
            <p style="font-size: 28px; font-weight: 700; letter-spacing: 4px;">{code}</p>
        </body>
    </html>
    """.format(code=verification_code)
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"{receiver_email} 로 이메일 전송 성공!")
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    send_email("hahahafunnydude@gmail.com", "123456")
