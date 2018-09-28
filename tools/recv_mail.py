#!/usr/bin/env python
# -*- coding: utf-8 -*-
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header 
import smtplib
from skimage import io

def mail_to_me(mailcontent,im_arr=None):
	subject = 'Error提醒'
	msg = MIMEText(mailcontent, 'plain', 'utf-8')
	msg['Subject'] = Header(subject, 'utf-8')
	msg['From'] = 'Akaisora<akaisorani@126.com>'
	msg['To'] = "1224067801@qq.com"
	
	from_addr="akaisorani@126.com"
	pw="HANSMTP126"
	smtp_server="smtp.126.com"
	to_addr="1224067801@qq.com"

	
	server = smtplib.SMTP(smtp_server, 25)
	server.set_debuglevel(0)
	server.login(from_addr, pw)
	server.sendmail(from_addr, [to_addr], msg.as_string())
	server.quit()

if __name__=="__main__":	
	mail_to_me("mail from python")
	