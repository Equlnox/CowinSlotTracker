import smtplib
from secrets import GMAIL_APP_PASSWORD
EMAIL_ADDRESS="incognito.equinox@gmail.com"

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(EMAIL_ADDRESS, GMAIL_APP_PASSWORD)
    subject = "Test email using python"
    body = "Yay, email sent!"
    msg = f'Subject: {subject}\n\n{body}'
    smtp.sendmail(EMAIL_ADDRESS, "karnalprateek@gmail.com", msg)
