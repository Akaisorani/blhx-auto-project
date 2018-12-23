#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tools.pymail import *
from skimage import io
from PIL import ImageGrab,Image
import threading
import time,re,traceback
import sys
import numpy as np

listen_mail_active=False
self_addr="akaisorani@126.com"

def mail_to_me(subject,mailcontent,im_arr=None):
	img_filename=None
	if im_arr is not None:
		img_filename='test.png'
		io.imsave(img_filename,im_arr)
	send_mail(self_addr,subject,mailcontent,img_filename)

def get_screenshoot():
	img=ImageGrab.grab()
	img=np.asarray(img)
	return img
	
def execute_command(command):
	if command=="screen":
		img=get_screenshoot()
		filename="screenshot.png"
		io.imsave(filename,img)
		send_mail(self_addr,"Screenshot","",image=filename)
	else:
		ret=eval(command)
		send_mail(self_addr,"Command Result",str(ret))

def listen_mail_eval():
	global listen_mail_active
	
	Subject="check"
	From=self_addr
	while listen_mail_active:
		msg=receive_mail(Subject,From,40)
		if msg:
			text=get_texts(msg)
			text="".join(text)
			print("received mail:\n"+text)
			command_list=re.findall(r'\$(.*?)\$',text)
			if command_list:
				for command in command_list:
					try:
						execute_command(command)
					except Exception as e:
						traceback.print_exc()
						mail_to_me("command error",str(traceback.format_exc())+str(e))
		time.sleep(30)

def begin_watch():
	global t,listen_mail_active
	
	if not listen_mail_active:
		t=threading.Thread(target=listen_mail_eval)
		listen_mail_active=True
		t.start()
		print("begin_watch")		
	
def end_watch():
	listen_mail_active=False
	t.join()

if __name__=="__main__":	
	#mail_to_me("mail from python")
	#begin_watch()
	import cv2
	gm=get_screenshoot()
	cv2.imshow('gm',gm)
	cv2.waitKey(100000)