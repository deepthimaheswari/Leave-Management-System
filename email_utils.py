import smtplib
from email.message import EmailMessage

def send_email(to_email, subject, body, sender_email, app_password):
    """Sends an email using smtplib with the provided credentials."""
    if not sender_email or not app_password:
        print("Email credentials are not set. Skipping email.")
        return False
        
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
        return False