import smtplib, os, traceback, pytz, datetime, logging
from email.utils import COMMASPACE
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def smtp_connect(smtp):
    if smtp.ssl:
        smtp_connection = smtplib.SMTP_SSL(smtp.host, smtp.port)
    else:
        smtp_connection = smtplib.SMTP(smtp.host, smtp.port)
    
    smtp_connection.login(smtp.username, smtp.password)

    return smtp_connection

def smtp_send(smtp_conf, template, msg):
    logger = logging.getLogger(__name__)
    smtp_connection = smtp_connect(smtp_conf)
    
    msg['Subject'] = template.subject
    msg['From'] = template.sender
    recipients = [k for k, v in template.to.items() if v]
    msg['To'] = COMMASPACE.join(recipients)

    smtp_connection.sendmail(
            template.sender,
            recipients,
            msg.as_string()
        )
    smtp_connection.quit()
    logger.info("Email sent")
    

def send_email(smtp_conf, template, msg_body_text, msg_body_html):
    msgtext = '\n'.join(msg_body_text)
    msghtml = '<br>'.join(msg_body_html)


    msg = MIMEMultipart(
        "alternative",
        None,
        [MIMEText(msgtext),
        MIMEText(msghtml,'html')]
    )

    smtp_send(smtp_conf, template, msg)

def send_email_text(smtp_conf, template, msg_body_text):
    msgtext = '\n'.join(msg_body_text)

    msg = MIMEText(msgtext)

    smtp_send(smtp_conf, template, msg)


def send_email_html(smtp_conf, template, msg_body_html):
    msghtml = '<br>'.join(msg_body_html)
    send_email_html_raw(smtp_conf, template, msghtml)

def send_email_html_raw(smtp_conf, template, msghtml):

    msg = MIMEText(msghtml,'html')

    smtp_send(smtp_conf, template, msg)

def send_email_exception(subject, ex, logs=[]):
    logger = logging.getLogger(__name__)
    try:
        erc = ExceptionReportingConfig()
        message = [get_timestamp()]
        message.append(erc.format_except(ex))
        message.extend(logs)
        logger.warn(message)
        template = EmailTemplate(
            to = {os.environ['EMAIL_NOTIFY_TO']: True},
            sender = os.environ['EMAIL_NOTIFY_FROM'],
            subject = subject
        )
        
        send_email_text(SMTPConfig(), template, message)
    except Exception:
        logger.error(traceback.format_exc())

def format_date(d):
    return d.strftime('%y-%m-%d %H:%M:%S %Z')

def get_timestamp():

    if 'TZ_NAME' in os.environ:
        tz_name = os.environ['TZ_NAME']
    else:
        tz_name = 'UTC'
    timezone = pytz.timezone(tz_name)
    return format_date(datetime.datetime.now(timezone))


class EmailTemplate:

    def __init__(self, sender, to, subject):
        self.sender = sender
        self.to = to
        self.subject = subject

class ExceptionReportingConfig:
    def __init__(self):
        if  not "EXCEPTION_FORMATTER" in  os.environ:
            self.format_except = self.traceback
        elif os.environ['EXCEPTION_FORMATTER'] == 'traceback':
            self.format_except = self.traceback
        elif os.environ['EXCEPTION_FORMATTER'] == 'unpack_except':
            self.format_except = self.unpack_except
        else:
            self.format_except = self.traceback


    def traceback(self, ex):
        traceback.format_exc()

    def unpack_except(self, ex):
        result = []
        result.append(type(ex).__name__)
        for arg in ex.args:
            if isinstance(arg, Exception):
                result.extend(self.unpack_except(arg))
            elif isinstance(arg, list):
                result.append(''.join(arg))
            else:
                result.append(str(arg))
        return '\n'.join(result)

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