#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import os,sys
import random,copy,time
from PIL import ImageGrab,Image
import numpy as np
from matplotlib import pyplot as plt
from skimage import io,feature,morphology,filters,color,measure
# import pytesseract
import win32api,win32con,win32gui
import queue
from tools.get_grid_center import get_grid_center
from tools.get_obj_pos import get_obj_pos
from tools.get_grid_status import get_grid_status
from tools.wintools import *
from tools.mail import mail_to_me
from tools.temp_match import surf_detect, pre_detect
import traceback

class Obj(object):
	def __init__(self,img,kp=None,des=None):
		self.img=img
		self.kp=kp
		self.des=des

def debugim(im):
	imm=np.asarray(im)
	io.imshow(imm)
	plt.show()

# window 700 430	

def load_obj_ims():
	global im,height,width,obj_labels
	
	objs_list=[]
	
	labels_list=['likeqianwang','likeqianwang2','queren',
		'chuji','dahuoquanshen','dianjijixu','dahuoquanshen2','yingji',
		'fleet1','fleet2','qiehuan','yanxizuozhan','gaojiyanxi','zhidaole']
	
	# labels_list=["chuji.png","chujiinmap.png","dahuoquansheng.png","zilv.png",
	# "likeqianwang.png","likeqianwang2.png","likeqianwang4.png",
	# "huodedaoju.png","queren.png","6-2hard.png","xingneng.png",
	# "yingji.png","guibi.png","queding.png",
	# "zhanshunianya.png","zhenglikuozhan.png"]+objs_list
	
	#labels_list=[x+'.PNG' for x in labels_list]
	#objs_list=[x+'.PNG' for x in objs_list]
	labels_list=labels_list+objs_list

	obj_labels=dict();#im_labels_gray=dict();im_labels_rgbvec=dict()
	for filename in labels_list:
		name=os.path.splitext(filename)[0]
		img=io.imread("./res/"+filename+'.PNG')
		if len(img.shape)==3 and img.shape[2]==4:img=np.delete(img,3,2)
		obj_labels[name]=Obj(img)
		pre_detect(obj_labels[name])
		#im_labels_gray[name]=color.rgb2gray(im_labels[name])
		#im_labels_rgbvec[name]=np.zeros(3,dtype=np.int32)
		#for i in range(3):im_labels_rgbvec[name][i]=int(im_labels[name][:,:,i].mean())

def get_im_xy():
	# im=io.imread('map_sample.png')
	# x=0;y=0
	im=ImageGrab.grab()
	im=np.asarray(im)
	pos1,pos2=get_window_pos()
	if pos1==(-1,-1):
		messagebox("Can't find game window!")
		raise
	im=im[pos1[1]:pos2[1],pos1[0]:pos2[0]].copy()
	x,y=pos1[1],pos1[0]
	#if len(im.shape)==3 and im.shape[2]==4:im=np.delete(im,3,2)
	return im,x,y


def trans_to_screenpos(inpos):
	return (inpos[1]+sty,inpos[0]+stx)

def click_lab(pos):
	click_pos=trans_to_screenpos(pos)
	mouse_click(click_pos,0.5)

def simple_CU():
	for name,obj in obj_labels.items():
		pos,cnt=surf_detect(obj,gm)
		if cnt>=3:
			click_lab(pos)
			return name
	return None
		
# MAIN PROCESS----------------------------
time.sleep(2)
print("start")
load_obj_ims()
search_fail=0

while True:
	gm,stx,sty=get_im_xy()
	height=gm.shape[0];width=gm.shape[1]
	gm=Obj(gm)
	pre_detect(gm)
	print("*",end="");sys.stdout.flush()
	try:
		res=simple_CU()
		if res:
			print(res)
			search_fail=0
		else:
			search_fail+=1
		if search_fail>100:
			mail_to_me("search_fail>100")
			search_fail=0
	except Exception as e:
		print(e)
		print("Error")
		traceback.print_exc()
		try:
			mail_to_me(str(traceback.format_exc())+str(e))
		except Exception as e2:
			pass
		time.sleep(600)
	time.sleep(1.5)
	
	
	
	
	
	# DEBUG 
im_match_test=im.copy()

for i in range(grid_h):
	for j in range(grid_w):
		im_match_test[grid_center[i][j][0]-2:grid_center[i][j][0]+3,grid_center[i][j][1]-2:grid_center[i][j][1]+3]=[0,0,0]
for name,lis in obj_pos.items():
	for pos in lis:
		im_match_test[pos[0]:pos[0]+10,pos[1]:pos[1]+10]=[255,0,0]
im_match_test[test_click_pos[0]:test_click_pos[0]+10,test_click_pos[1]:test_click_pos[1]+10]=[0,255,0]

debugim(im_match_test)
io.imsave('info.png',im_match_test)










			



#OCR
# mess=pytesseract.image_to_string(Image.open('map_sample.png'))
# print(mess)

#Image to arr
# im=np.asarray(im)

#轮廓分离
# contours=measure.find_contours(edges,0.5)
# print(contours[0])
# for contour in contours:
	# plt.imshow(contour)
	# plt.show()

#win32api
# win32api.MessageBox(win32con.NULL,'hello world!','fuck you!',win32con.MB_OK)