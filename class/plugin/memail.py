# coding: utf-8

import smtplib

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send(smtp_host, smtp_port, username, password, to_mail, subject, content):

    smtp = smtplib.SMTP()
    smtp.connect(smtp_host, port=smtp_port)
    smtp.login(user=username, password=password)

    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = _format_addr(username)
    msg['To'] = _format_addr(to_mail)
    msg['Subject'] = Header(subject, 'utf-8').encode()

    smtp.sendmail(from_addr=username, to_addrs=to_mail, msg=msg.as_string())
    return True


def sendSSL(smtp_host, smtp_port, username, password, to_mail, subject, content):

    smtp = smtplib.SMTP_SSL(smtp_host, port=smtp_port)
    smtp.login(user=username, password=password)

    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = _format_addr(username)
    msg['To'] = _format_addr(to_mail)
    msg['Subject'] = Header(subject, 'utf-8').encode()

    smtp.sendmail(from_addr=username, to_addrs=to_mail, msg=msg.as_string())
    smtp.quit()
    return True
