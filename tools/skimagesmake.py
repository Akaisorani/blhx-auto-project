#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
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

def debugim(im):
	imm=np.asarray(im)
	io.imshow(imm)
	plt.show()

def load_obj_ims():
	global im,im_gray,im_objs,im_objs_gray,height,width,im_labels,im_labels_gray
	objs_list=["enemy_boss.png","enemy_boss2.png","enemy_cv.png","enemy_dd.png","enemy_dd2.png","enemy_dd3.png","enemy_dd4.png",
	"enemy_bb.png","enemy_bb2.png","enemy_cv2.png","enemy_cv3.png","enemy_cv4.png"]
	labels_list=["chujiinmap.png","yingji.png","dahuoquansheng.png","zilv.png",
	"huodedaoju.png","queren.png","3-4.png","xingneng.png",
	"likeqianwang2.png"]+objs_list
	im_objs=dict();im_objs_gray=dict()
	for filename in objs_list:
		name=os.path.splitext(filename)[0]
		im_objs[name]=io.imread(filename)
		if len(im_objs[name].shape)==3 and im_objs[name].shape[2]==4:im_objs[name]=np.delete(im_objs[name],3,2)
		im_objs_gray[name]=color.rgb2gray(im_objs[name])
		im_objs[name]=im_objs[name][:,:,0].reshape((im_objs[name].shape[0],im_objs[name].shape[1]))
	im_labels=dict();im_labels_gray=dict()
	for filename in labels_list:
		name=os.path.splitext(filename)[0]		
		im_labels[name]=io.imread(filename)
		if len(im_labels[name].shape)==3 and im_labels[name].shape[2]==4:im_labels[name]=np.delete(im_labels[name],3,2)
		im_labels_gray[name]=color.rgb2gray(im_labels[name])
		im_labels[name]=im_labels[name][:,:,0].reshape((im_labels[name].shape[0],im_labels[name].shape[1]))

def get_im_xy():
	global im_red
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
	im_red=im[:,:,0].reshape((im.shape[0],im.shape[1]))
	return im,x,y

def bfs_find_path(grid_status,st,ed):
	dire=((1,0),(-1,0),(0,-1),(0,1))
	walls={"hill","enemy_bb","enemy_cv","enemy_dd"}
	vis=np.zeros(grid_status.shape,dtype=np.bool)
	Q=queue.Queue()
	Q.put([st])
	vis[st]=True
	while not Q.empty():
		path=Q.get()
		x,y=path[-1]
		for dx,dy in dire:
			nx=x+dx;ny=y+dy
			if (nx,ny)==ed:return path+[(nx,ny)]
			if nx>=0 and nx<grid_status.shape[0] and ny>=0 and ny<grid_status.shape[1] and (grid_status[nx,ny] not in walls) and not vis[nx,ny]:
				Q.put(path+[(nx,ny)])				
				vis[nx,ny]=True
	return []
	
def map_CU(grid_status,obj_pos,grid_center):
	global test_click_pos
	self_pos=(-1,-1);boss_pos=(-1,-1);enemy_pos_lis=[]
	for i in range(grid_status.shape[0]):
		for j in range(grid_status.shape[1]):
			if grid_status[i,j]=="self":self_pos=(i,j)
			elif grid_status[i,j]=="enemy_boss":boss_pos=(i,j)
			elif grid_status[i,j] in {"enemy_bb","enemy_cv","enemy_dd"}:enemy_pos_lis.append((i,j))
	if self_pos==(-1,-1) or (boss_pos==(-1,-1) and enemy_pos_lis==[]):
		if self_pos==(-1,-1) and boss_pos==(-1,-1) and enemy_pos_lis==[] : 
			print("非地图");return -2
		else :
			print("地图信息不完整");return -1
	
	target_pos=(-1,-1)
	if boss_pos!=(-1,-1) and bfs_find_path(grid_status,self_pos,boss_pos)!=[]:
		target_pos=boss_pos
	else:
		maxlen=10000
		for enemy_pos in enemy_pos_lis:
			path=bfs_find_path(grid_status,self_pos,tuple(enemy_pos))
			if path!=[] and len(path)<maxlen:
				maxlen=len(path)
				target_pos=enemy_pos
	path=bfs_find_path(grid_status,self_pos,tuple(target_pos))
	dirsta=1
	now_pos=self_pos
	for i in range(1,len(path)):
		if path[i][1]==path[i-1][1]:
			dirsta=0
		if dirsta==0 and path[i][0]==path[i-1][0]:
			break
		now_pos=path[i]
	click_pos=grid_center[now_pos]
	print("goto ",now_pos)
	click_pos=trans_to_screenpos(click_pos)
	test_click_pos=tuple((click_pos[1],click_pos[0]))
	mouse_click(click_pos,0.5)
	# mouse_drag((click_pos),(click_pos+(-50,50)),0.5)

def simple_CU():
	if exist("enemy_boss"):click_lab("enemy_boss");return
	if exist("enemy_boss2"):click_lab("enemy_boss2");return
	for name in im_labels:
		if name!="yingji" and click_lab(name):print(name);return

def trans_to_screenpos(inpos):
	return (inpos[1]+sty,inpos[0]+stx)
	
def move_map_to_center(mapshape,grid_center):
	mapcenter=((grid_center[0][0]+grid_center[-1][0])//2,(grid_center[grid_center.shape[0]//2][1]+grid_center[grid_center.shape[0]//2][1])//2)
	imcenter=(mapshape[0]*335//564,mapshape[1]//2)
	mapcenter=trans_to_screenpos(mapcenter)
	imcenter=trans_to_screenpos(imcenter)
	mouse_drag(mapcenter,imcenter)

def exist(lab):
	result=feature.match_template(im_gray,im_labels_gray[lab]);
	resultrgb=feature.match_template(im_red,im_labels[lab]);
	if np.max(result)>0.8 and np.max(resultrgb)>0.8:
		return True
	else:
		return False

def click_lab(lab):
	result=feature.match_template(im_gray,im_labels_gray[lab]);
	resultrgb=feature.match_template(im_red,im_labels[lab]);
	if np.max(result)>0.8 and np.max(resultrgb)>0.8:
		print("click",lab)
		pos=np.unravel_index(np.argmax(result),result.shape)
		pos=(pos[0]+int(im_labels_gray[lab].shape[0]/2),pos[1]+int(im_labels_gray[lab].shape[1]/2))
		if lab=="xingneng":pos=(pos[0]-100,pos[1])
		click_pos=trans_to_screenpos(pos)
		mouse_click(click_pos,0.5)
		return True
	return False

def scene_judge(im,ilg):
	if exist("yingji") : return "map"
	for lab,img in ilg.items():
		if lab!="yingji" and click_lab(lab):return lab
	return "unknown"
# MAIN PROCESS----------------------------
time.sleep(2)
print("start")
load_obj_ims()
test_click_pos=(10,10)
while True:
	im,stx,sty=get_im_xy()
	im_gray=color.rgb2gray(im)
	height=im.shape[0];width=im.shape[1]
	print((height,width))
	try:
		pass
	except Exception as e:
		print(e)
		print("Error")	
	finally:
		time.sleep(1)
	simple_CU()
	
	if False:
		scene=scene_judge(im_gray,im_labels_gray)
		print(scene)
		try:
			# scene="map"
			if scene=="map":
				grid_center=get_grid_center(im)
				grid_h,grid_w=grid_center.shape[0],grid_center.shape[1]
				
				# im_match_test=im.copy()
				# for i in range(grid_h):
					# for j in range(grid_w):
						# im_match_test[grid_center[i][j][0]-2:grid_center[i][j][0]+3,grid_center[i][j][1]-2:grid_center[i][j][1]+3]=[0,0,0]

				# debugim(im_match_test)
				
				obj_pos=get_obj_pos(im_gray,im_objs_gray)
				for name,poslis in obj_pos.items():print(name,poslis)
				# for name,lis in obj_pos.items():
					# for pos in lis:
						# im_match_test[pos[0]:pos[0]+10,pos[1]:pos[1]+10]=[255,0,0]
				# debugim(im_match_test)
				
				# mouse_move((obj_pos["self"][0][1],obj_pos["self"][0][0]))
				grid_status=get_grid_status(grid_center,obj_pos)
				load_grid_data(grid_status,"3-4")
				print(grid_status)		
				sta=map_CU(grid_status,obj_pos,grid_center)
				if sta==-1 : move_map_to_center(im.shape,grid_center)
		except Exception as e:
			print(e)
			print("Error")
		finally:
			time.sleep(1)
	
	
	
	
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