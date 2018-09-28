#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
import random,copy,time
from PIL import ImageGrab,Image
import numpy as np
from matplotlib import pyplot as plt
from skimage import io,feature,morphology,filters,color,measure
# import pytesseract
import win32api,win32con,win32gui
import queue
from get_grid_center import get_grid_center
from get_obj_pos import get_obj_pos
from get_grid_status import get_grid_status
from wintools import *
from load_grid_data import load_grid_data
from mail import mail_to_me
import traceback

def debugim(im):
	imm=np.asarray(im)
	io.imshow(imm)
	plt.show()

# window 700 430	

def load_obj_ims():
	global im,im_gray,height,width,im_labels,im_labels_gray,im_labels_rgbvec,objs_order,labels_order
	
	objs_list=['enemy_boss','enemy_dd','enemy_cv','enemy_bb']
	# objs_list=["enemy_boss.png","enemy_cv.png","enemy_bb.png","enemy_bb2.png","question.png",
	# "enemy_dd.png","enemy_gold.png",
	# ]
	
	labels_list=['yisege','kunnan','D2','likeqianwang','likeqianwang2','qianting_shoot','zilvoff',
		'chuji','dahuoquanshen','dianjijixu','queren','dahuoquanshen2','yingji',
		'fleet1','fleet2','qiehuan']
	# labels_list=["chuji.png","chujiinmap.png","dahuoquansheng.png","zilv.png",
	# "likeqianwang.png","likeqianwang2.png","likeqianwang4.png",
	# "huodedaoju.png","queren.png","6-2hard.png","xingneng.png",
	# "yingji.png","guibi.png","queding.png",
	# "zhanshunianya.png","zhenglikuozhan.png"]+objs_list
	labels_list=[x+'.PNG' for x in labels_list]
	objs_list=[x+'.PNG' for x in objs_list]
	labels_list=labels_list+objs_list

	im_labels=dict();im_labels_gray=dict();im_labels_rgbvec=dict()
	for filename in labels_list:
		name=os.path.splitext(filename)[0]		
		im_labels[name]=io.imread("./res18-7/"+filename)
		if len(im_labels[name].shape)==3 and im_labels[name].shape[2]==4:im_labels[name]=np.delete(im_labels[name],3,2)
		im_labels_gray[name]=color.rgb2gray(im_labels[name])
		im_labels_rgbvec[name]=np.zeros(3,dtype=np.int32)
		for i in range(3):im_labels_rgbvec[name][i]=int(im_labels[name][:,:,i].mean())
	
	objs_order=list(map(lambda x:os.path.splitext(x)[0],objs_list))
	labels_order=list(map(lambda x:os.path.splitext(x)[0],labels_list))

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
	if len(im.shape)==3 and im.shape[2]==4:im=np.delete(im,3,2)
	return im,x,y

def decide_fleet():
	if exist("enemy_boss")!=(-1,-1):
		print('exist boss')
		if exist('fleet2')!=(-1,-1):
			click_lab('qiehuan')
			return True
	else:
		print('nnot exist boss')
		if exist('fleet1')!=(-1,-1):
			print('cliais qiehuan')
			click_lab('qiehuan')
			return	True
	return False

def simple_CU():
	if decide_fleet():return
	print('exist yingji')
	if exist("yingji")!=(-1,-1):
		if exist("guibi")!=(-1,-1):
			match_order=labels_order
		else : 
			if cjcnt>=7 :solve_boss_behind()
			if cjcnt>9 :mail_to_me("boss behind");solve_boss_behind(alw_sleep=True)
			match_order=objs_order
	else: match_order=labels_order
	for name in match_order:
		if name!="yingji" and click_lab(name):return
		
def simple_CU2():
	if click_lab("enemy_boss") or click_lab("enemy_boss") or click_lab("enemy_boss") or click_lab("enemy_boss"):return
	if exist("yingji")!=(-1,-1):
		if exist("guibi")!=(-1,-1):
			match_order=labels_order
		else : 
			if cjcnt>=7 :solve_boss_behind()
			if cjcnt>9 :mail_to_me("boss behind");solve_boss_behind(alw_sleep=True)
			match_order=objs_order
	else: match_order=labels_order
	for name in match_order:
		if name!="yingji" and click_lab(name):return

def solve_boss_behind(alw_sleep=False):
	global im,stx,sty,im_gray,height,width,moved
	if exist("enemy_boss")!=(-1,-1):return
	if exist("yingji") and not moved:
		stpos=(im.shape[0]//2,im.shape[1]//2)
		edpos=(stpos[0]+37,stpos[1]+84)
		stpos=trans_to_screenpos(stpos)
		edpos=trans_to_screenpos(edpos)
		mouse_drag(stpos,edpos,delay=8)
		moved=True
		im,stx,sty=get_im_xy()
		im_gray=color.rgb2gray(im)
		height=im.shape[0];width=im.shape[1]
		if exist("enemy_boss")!=(-1,-1) or exist("enemy_boss")!=(-1,-1) or exist("enemy_boss")!=(-1,-1) or exist("enemy_boss")!=(-1,-1) or exist("enemy_boss")!=(-1,-1):return
		pos=(182,766)
		pos=trans_to_screenpos(pos)
		mouse_click(pos,delay=20)
		im,stx,sty=get_im_xy()
		im_gray=color.rgb2gray(im)
		height=im.shape[0];width=im.shape[1]
		if exist("enemy_boss")!=(-1,-1) or exist("enemy_boss")!=(-1,-1) or exist("enemy_boss")!=(-1,-1) or exist("enemy_boss")!=(-1,-1) or exist("enemy_boss")!=(-1,-1):return
	if alw_sleep:
		mail_to_me("solve boss behind fail,begin sleep")
		time.sleep(10000)
def adjust_6_3():
	global im,stx,sty,im_gray,height,width,moved
	if not moved and exist("yingji") :
		stpos=(im.shape[0]//2,im.shape[1]//2)
		edpos=(stpos[0]+37,stpos[1]+84)
		stpos=trans_to_screenpos(stpos)
		edpos=trans_to_screenpos(edpos)
		mouse_drag(stpos,edpos,delay=8)
		moved=True
		im,stx,sty=get_im_xy()
		im_gray=color.rgb2gray(im)
		height=im.shape[0];width=im.shape[1]	

def trans_to_screenpos(inpos):
	return (inpos[1]+sty,inpos[0]+stx)
	

def exist(lab,match_bound=0.8,vecdis_bound=500):
	if lab not in im_labels_gray:return False
	result=feature.match_template(im_gray,im_labels_gray[lab]);
	if np.max(result)>match_bound:
		pos=np.unravel_index(np.argmax(result),result.shape)
		# print(result[pos])
		im_piece=im[pos[0]:pos[0]+im_labels[lab].shape[0],pos[1]:pos[1]+im_labels[lab].shape[1]]
		im_piece_rgbvec=np.zeros(3,dtype=np.int32)
		for i in range(3):im_piece_rgbvec[i]=int(im_piece[:,:,i].mean())
		# print("im_piece_vecor ",im_piece_rgbvec,"\nlab ",im_labels_rgbvec[lab])
		dis=im_piece_rgbvec-im_labels_rgbvec[lab]
		dis=np.dot(dis,dis)
		pos=(pos[0]+im_labels[lab].shape[0]//2,pos[1]+im_labels[lab].shape[1]//2)
		if dis<vecdis_bound : 
			return pos
		else : return (-1,-1)
	else:
		return (-1,-1)

def click_lab(lab):
	global cjcnt,search_fail,moved
	if lab not in im_labels_gray:return False
	#result=feature.match_template(im_gray,im_labels_gray[lab]);
	x,y=exist(lab)
	print(x,y)
	if x!=-1:
		print("click",lab)
		if lab=="xingneng":x-=100
		if lab=="zhenglikuozhan":mail_to_me("zhenglikuozhan,begin sleep");time.sleep(10000)
		if lab=="3-4":cjcnt=0;moved=False
		if lab=="chujiinmap":cjcnt+=1
		search_fail=0
		click_pos=trans_to_screenpos((x,y))
		mouse_click(click_pos,0.5)
		#log_click(lab)
		return True
	return False

def log_click(lab):
	global timelast
	freq=dict()
	if not os.path.exists("freq.txt"):open("freq.txt","w").close()
	with open("freq.txt","r") as f:
		lines=f.readlines()
		for line in lines:
			name,num=line.split()
			freq[name]=int(num)
	if lab in freq:
		freq[lab]+=1
	else: freq[lab]=1
	dic2str=""
	with open("freq.txt","w") as f:
		for name,num in freq.items():
			dic2str+=name+" "+str(num)+"\n"
		f.write(dic2str)
	if (time.time()-timelast)>20*60 : 
		mail_to_me(dic2str)
		timelast=time.time()

# MAIN PROCESS----------------------------
time.sleep(2)
print("start")
load_obj_ims()
test_click_pos=(10,10)
timelast=time.time()
cjcnt=0
search_fail=0
moved=False
status={"task":"None","scene":"main"}

while True:
	im,stx,sty=get_im_xy()
	im_gray=color.rgb2gray(im)
	height=im.shape[0];width=im.shape[1]
	print("*",end="");sys.stdout.flush()
	search_fail+=1
	# x,y=exist("chujiinmap")
	# if x!=-1:
		# print("x,y ",x,y)
		# im_test=im.copy()
		# im_test[x:x+10,y:y+10]=[255,0,0]
		# debugim(im_test)
	# break
	try:
		simple_CU()
		if search_fail>20:
			mail_to_me("search_fail>20")
			solve_boss_behind(alw_sleep=True)
	except Exception as e:
		print(e)
		print("Error")
		traceback.print_exc()
		try:
			mail_to_me(str(traceback.format_exc())+str(e))
		except Exception as e2:
			pass
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