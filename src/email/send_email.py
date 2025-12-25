import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from datetime import date
load_dotenv()

def send_email(output):
    try:
        with smtplib.SMTP('smtp.hostinger.com', 587) as s:
            s.starttls()
            email_password = os.getenv("EMAIL_PASSWORD")
            s.login("pradeep@agileai.in",email_password)
            today = date.today()
            formatted_date = today.strftime("%d-%b-%Y")
            message = EmailMessage()
            message['Subject'] = f'BSE Stock trading signals on {formatted_date}'
            message['From'] = "pradeep@agileai.in"
            message['To'] = "pradeepprajan@agileapps.in"
            message.set_content(output)
            s.send_message(message)
            s.quit()
    except Exception as e:
        print(f"An error occurred while sending email: {e}")

        