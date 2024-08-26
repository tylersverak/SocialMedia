
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage 
from email.mime.application import MIMEApplication 
from email.mime.multipart import MIMEMultipart 
import smtplib 
import os
from secret import gmailpasswords as secrets

def email_content():
    # creating email message
    msg = MIMEMultipart()
    msg['Subject'] = "html email"
    content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            color: #333333;
            margin: 20px;
        }
        h1 {
            color: #4CAF50;
        }
        p {
            font-size: 16px;
        }
    </style>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>This is a simple HTML email.</p>
    <p>Feel free to customize this template as needed.</p>
</body>
</html>
    """
    msg.attach(MIMEText(content, "html"))
    print("Email prepared...")

def main():

    # setup connection to smtp server
    smtp = smtplib.SMTP('smtp.office365.com', 587)
    smtp.ehlo() 
    smtp.starttls() 
    smtp.login(secrets.MYADDRESS, secrets.APPPASSWORD)
    print("Successful connection...")

    # create the actual email contents
    msg = email_content()

    for target_addr in secrets.TARGETADDRESSES:
        smtp.sendmail(from_addr=secrets.MYADDRESS,
                    to_addrs=target_addr, msg=msg.as_string())
    smtp.quit()
    print("Email sent, connection close, all done!")

if __name__=="__main__":
    main()
