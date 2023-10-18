import smtplib
from email.mime.text import MIMEText


def send_email(to_email, new_password):
    # Configure your email server and credentials here
    smtp_server = 'smtp.mail.ru'
    smtp_port = 465
    smtp_username = 'hackaton.postmail@mail.ru'
    smtp_password = 'AESXAEg5Sjw2Q4yR1EjD'

    # Create an SMTP connection
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
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
