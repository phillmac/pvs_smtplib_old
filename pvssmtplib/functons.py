import smtplib, os
from email.utils import COMMASPACE
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(smtp, template, msg_body_text, msg_body_html):
        s = smtplib.SMTP_SSL(smtp.host, smtp.port)
        s.login(smtp.username, smtp.password)

        msgtext = '\n'.join(msg_body_text)
        msghtml = '<br>'.join(msg_body_html)


        msg = MIMEMultipart(
            "alternative",
            None,
            [MIMEText(msgtext),
            MIMEText(msghtml,'html')]
        )

        msg['Subject'] = template.subject
        msg['From'] = template.sender
        recivers = [k for k, v in template.to.items() if v]
        msg['To'] = COMMASPACE.join(recivers)

        s.sendmail(
            template.sender,
            template.to,
            msg.as_string()
        )
        s.quit()
        print("Email sent")

def send_email_text(smtp, template, msg_body_text):
        s = smtplib.SMTP_SSL(smtp.host, smtp.port)
        s.login(smtp.username, smtp.password)

        msgtext = '\n'.join(msg_body_text)

        msg = MIMEText(msgtext)

        msg['Subject'] = template.subject
        msg['From'] = template.sender
        recivers = [k for k, v in template.to.items() if v]
        msg['To'] = COMMASPACE.join(recivers)

        s.sendmail(
            template.sender,
            template.to,
            msg.as_string()
        )
        s.quit()
        print("Email sent")

def send_email_html(smtp, template, msg_body_html):
        msghtml = '<br>'.join(msg_body_html)
        send_email_html_raw(smtp, template, msghtml)

def send_email_html_raw(smtp, template, msghtml):
        s = smtplib.SMTP_SSL(smtp.host, smtp.port)
        s.login(smtp.username, smtp.password)

        msg = MIMEText(msghtml,'html')

        msg['Subject'] = template.subject
        msg['From'] = template.sender
        recivers = [k for k, v in template.to.items() if v]
        msg['To'] = COMMASPACE.join(recivers)

        s.sendmail(
            template.sender,
            template.to,
            msg.as_string()
        )
        s.quit()
        print("Email sent")

class EmailTemplate:

    def __init__(self, sender, to, subject):
        self.sender = sender
        self.to = to
        self.subject = subject

class SMTPConfig:

    def __init__(self):
        self.host = os.environ['SMTP_HOST']
        self.port = os.environ['SMTP_PORT']
        if os.environ['SMTP_USE_SSL'] == "1":
            self.ssl = True
        elif os.environ['SMTP_USE_SSL'].lower() == "true":
            self.ssl = True
        elif os.environ['SMTP_USE_SSL'].lower() == "yes":
            self.ssl = True
        elif os.environ['SMTP_USE_SSL'].lower() == "on":
            self.ssl = True
        else:
            self.ssl = False
        self.username = os.environ['SMTP_USER']
        self.password = os.environ['SMTP_PASSWD']