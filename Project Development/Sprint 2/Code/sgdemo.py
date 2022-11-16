import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    from_email='works.suryav@gmail.com',
    to_emails='suryavelu2112@gmail.com',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient("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")
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)