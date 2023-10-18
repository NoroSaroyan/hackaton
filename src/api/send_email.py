import smtplib
from email.mime.text import MIMEText


def send_email(to_email, new_password):
    # Configure your email server and credentials here
    smtp_server = 'your-smtp-server.com'
    smtp_port = 587
    smtp_username = 'your-username'
    smtp_password = 'your-password'

    # Create an SMTP connection
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    # Compose the email message
    subject = "Password Reset"
    body = f"Your new password is: {new_password}"
    message = MIMEText(body, 'plain')
    message['From'] = smtp_username
    message['To'] = to_email
    message['Subject'] = subject

    # Send the email
    server.sendmail(smtp_username, to_email, message.as_string())

    # Close the SMTP connection
    server.quit()
