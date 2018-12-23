#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import os,sys
import random,copy,time,datetime
from PIL import ImageGrab,Image
import numpy as np
from matplotlib import pyplot as plt
from skimage import io,feature,morphology,filters,color,measure
# import pytesseract
import win32api,win32con,win32gui
import queue
from tools.wintools import *
from tools.mail import mail_to_me,begin_watch,end_watch
from tools.object_detect import Object_detect
import traceback
import logging  # 引入logging模块
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s',datefmt='%H:%M:%S')  # logging.basicConfig函数对日志的输出格式及方式做相关配置
import myconfig as config

class Obj(object):
	def __init__(self,img=None,name=None,kp=None,des=None,pos=None):
		self.img=img
		self.kp=kp
		self.des=des
		self.name=name
		self.pos=pos

def debugim(im):
	imm=np.asarray(im)
	io.imshow(imm)
	plt.show()

# Tools

def remove_alpha(img):
	if len(img.shape)==3 and img.shape[2]==4:
		return np.delete(img,3,2)
	else:
		return img
		
def rgb2bgr(img):
	return img[...,::-1]

def bgr2rgb(img):
	return img[...,::-1]
	
def get_im_xy():
	'''get the screenshot of the game window, and its left up corner position'''
	pos1,pos2=get_window_pos()
	if pos1==(-1,-1):
		messagebox("Can't find game window!")
		raise
	# ImageGrab got a RGB img(PIL)
	im=ImageGrab.grab((pos1[0],pos1[1],pos2[0],pos2[1]))
	im=np.asarray(im)
	im=rgb2bgr(im)
	x,y=pos1[1],pos1[0]
	return im,x,y

def get_gm():
	global gm,stx,sty
	gm,stx,sty=get_im_xy()
	gm=Obj(gm,'gm')
	obj_dect.pre_detect(gm)
	return gm

def trans_to_screenpos(inpos):
	global stx,sty
	return (inpos[1]+sty,inpos[0]+stx)

def drag_map(obj1,obj2):
	pos1=trans_to_screenpos(exist(obj1))
	pos2=trans_to_screenpos(exist(obj2))
	mouse_drag(pos1,pos2,0.5)
	
def exist(obj):
	''' return the postion of the obj in the window, if not exists, return None'''
	if isinstance(obj,str):
		if obj in obj_labels:
			return exist_obj(obj_labels[obj])
		else:
			logging.error('fake obj name '+obj)
			return None
	elif isinstance(obj,Obj):
		return exist_obj(obj)
	
	return None

def exist_obj(obj):
	pos=None
	gm=get_gm()
	if obj.img is not None:
		pos,score=obj_dect.sift_detect(obj,gm)
		logging.info("exist %s : "%obj.name+str(pos))
	elif obj.pos:
		pos=(int(gm.img.shape[0]*obj.pos[0]),int(gm.img.shape[1]*obj.pos[1]))
	return pos
	
def get_higher_score_lab(labs):
	maxlab=None
	maxscore=0
	gm=get_gm()
	for lab in labs:
		pos,score=obj_dect.sift_detect(obj_labels[lab],gm)
		if score>maxscore:
			maxscore=score
			maxlab=lab
	return maxlab
	
def click(obj):
	''' click labels,obj or postion'''
	if isinstance(obj,str):
		return click_obj(obj_labels[obj])
	elif isinstance(obj,Obj):
		return click_obj(obj)
	elif isinstance(obj,tuple):
		return click_pos(obj)
	else:
		return False
	
def click_pos(pos):
	pos=trans_to_screenpos(pos)
	mouse_click(pos,1.7)
	return True

def click_obj(obj):
	pos=exist(obj)
	if pos:
		click_pos(pos)
		logging.debug('click '+str(pos))
		return True
	else:
		return False

def trans(lab1,lab2):
	cnt=0
	while not exist(lab2):
		click(lab1)
		cnt+=1
		if cnt>100:
			logging.error("trans from %s to %s failed"%(lab1,lab2))
			raise ValueError("trans error")

def waitfor(lab,maxnum=3600):
	cnt=0
	while not exist(lab):
		time.sleep(1)
		cnt+=1
		if cnt>maxnum:
			raise ValueError('waitfor too much time')

def waitforclick(lab,maxnum=3600):
	waitfor(lab,maxnum)
	click(lab)
# Logics
def go_home():
	logging.info('go_home')
	while not exist('biandui'):
		[click(p) for p in ['return','X']]
		time.sleep(0.6)
	logging.info('reached home')
	
def enter_meiritiaozhan():
	if exist('logo_meiritiaozhan'):return True
	go_home()
	trans('home_chuji','meiritiaozhan')
	trans('meiritiaozhan','logo_meiritiaozhan')

def enter_yanxi():
	if exist('logo_yanxi'):return True
	go_home()
	trans('home_chuji','yanxi')
	trans('yanxi','logo_yanxi')
	time.sleep(3)
	
def enter_kunnan():
	if not exist('putong'):
		if exist('kunnan'):click('kunnan')
		else:
			go_home()
			click('home_chuji')
			if exist('kunnan'):click('kunnan')

def enter_putong():
	if not exist('kunnan'):
		if exist('putong'):click('putong')
		else:
			go_home()
			click('home_chuji')
			if exist('putong'):click('putong')
			
def todays_meiri():
	date_today=datetime.datetime.now().strftime('%A')
	meiri_labs=[]
	meiri_labs.append('meiri1-7')
	if date_today in ['Monday','Thursday','Sunday']:meiri_labs.append('meiri147')
	if date_today in ['Tuesday','Friday','Sunday']:meiri_labs.append('meiri257')
	if date_today in ['Wednesday','Saturday','Sunday']:meiri_labs.append('meiri367')
	return meiri_labs

def do_meiritiaozhan():
	meiri_labs=todays_meiri()
	battle_cfg={
		'fleet':'fleet2'
	}
	
	for tiaozhantype in meiri_labs:
		enter_meiritiaozhan()
		click(tiaozhantype)
		click(tiaozhantype)
		if exist('wrong_action'):
			time.sleep(3)
			continue
		for cs in range(3):
			if tiaozhantype=='meiri1-7':
				click('meiri_lis2')
			else:
				click('meiri_lis1')
			if exist('wrong_action'):
				time.sleep(3)
				break
			do_zhandou(battle_cfg)
		go_home()
		check_mission()

def do_yanxi():
	battle_cfg={}
	for i in range(10):
		enter_yanxi()
		click('yanxi_lis1')
		if exist('wrong_action'):
			time.sleep(3)
			break
		click('kaishiyanxi')
		do_zhandou(battle_cfg)
		go_home()
	check_mission()
		
def do_kunnan(level):
	battle_cfg={
		'road_fleet':'fleet1',
		'boss_fleet':'fleet1'
	}	
	chap=int(level.split('-')[0])
	for i in range(3):
		enter_kunnan()
		choose_chapter(chap)
		click(level)
		click('likeqianwang')
		click('likeqianwang2')
		if exist('wrong_action'):
			break
		do_map(battle_cfg)
	go_home()
	check_mission()
	
def do_putong(level):
	battle_cfg={
		'road_fleet':'fleet1',
		'boss_fleet':'fleet2'
	}	
	chap=int(level.split('-')[0])
	for i in range(3):
		enter_putong()
		choose_chapter(chap)
		click(level)
		click('likeqianwang')
		click('likeqianwang2')
		if exist('wrong_action'):
			break
		do_map(battle_cfg)
		time.sleep(2)
	go_home()
	check_mission()
	
def do_situertedexiaoyan():
	battle_cfg={
		'road_fleet':'fleet2',
		'boss_fleet':'fleet1'
	}		
	# 进入sp
	if not exist('stet_sp3'):
		go_home()
	trans('situertedexiaoyan','stet_sp3')
	click('stet_sp3')
	click('likeqianwang')
	click('likeqianwang2')
	if exist('wrong_action'):
		return
	do_map(battle_cfg)
	time.sleep(5)
	
def do_map(battle_cfg):
	current_fleet_num=1
	boss_appeared=False
	while not exist('logo_chuji'):
		time.sleep(1)
		if exist('enemy_boss'):
			boss_appeared=True
			current_fleet_num=choose_fleet_out(current_fleet_num,battle_cfg['boss_fleet'])
		if not boss_appeared:
			current_fleet_num=choose_fleet_out(current_fleet_num,battle_cfg['road_fleet'])		
		target_enemy=None
		for enemy in config.enemy_list:
			if exist(enemy):
				target_enemy=enemy
				break
		clicked=False
		if target_enemy:
			clicked|=bool(click(target_enemy))
		else:
			reslis=[click(p) for p in ['guibi','queren','zhidaole']]
			for res in reslis:clicked|=bool(res)
		time.sleep(2)
		if exist('chuji'):
			do_zhandou()
		solve_boss_behiend()
		if clicked:
			time.sleep(10)
			
		
		
	
def do_zhandou(battle_cfg={}):
	# prepare battle
	click('zilvoff')
	if 'fleet' in battle_cfg and battle_cfg['fleet'] is not None:choose_fleet_in(battle_cfg['fleet'])
	waitfor('chuji',5)
	click('chuji')
	# in battle
	time.sleep(10)
	click('qianting_shoot')
	# end battle
	waitforclick('dahuoquanshen')
	click('dianjijixu')
	click('dianjijixu')
	click('youzhang')
	waitforclick('dahuoquanshen2')
	waitforclick('queren')
	time.sleep(2)

def choose_chapter(chap):
	if not exist('logo_chap%d'%chap):
		for i in range(8):
			click('zuozhang')
		for i in range(chap-1):
			click('youzhang')
	
def choose_fleet_in(target_fleet):
	now_fleet=get_higher_score_lab(['fleet1','fleet2'])
	if not now_fleet:raise ValueError('cannot detect current fleet')
	if target_fleet=='fleet1' and now_fleet=='fleet2':
		click('zuofleet')
	elif target_fleet=='fleet2' and now_fleet=='fleet1':
		click('youfleet')
		
def choose_fleet_out(current_fleet_num,target_fleet):
	if ("fleet%d"%current_fleet_num)!=target_fleet:
		click('qiehuan')
		current_fleet_num=3-current_fleet_num	
	return current_fleet_num 

def check_mission():
	go_home()
	if exist('renwu_withex'):
		click('renwu_withex')
		while exist('lingqu'):
			click('lingqu')
			click('dianjijixu')
		go_home()

def solve_boss_behiend():
	direction=random.choice(['up','down','left','right'])
	drag_map('map_center','map_'+direction)

def load_obj_ims():
	'''define objects and load resources'''
	global obj_labels
	
	obj_labels=dict();
	for name in config.resources_list:
		img=cv2.imread(config.res_path+name+'.PNG')
		img=remove_alpha(img)
		obj_labels[name]=Obj(img,name=name)
		obj_dect.pre_detect(obj_labels[name])
	
	for name,pos_rate in config.position_list.items():
		obj_labels[name]=Obj(name=name,pos=pos_rate)

def init():
	global obj_dect
	obj_dect=Object_detect()
	load_obj_ims()

def begin_game():
	'''main process'''
	global gm,stx,sty,height,width
	
	time.sleep(2)
	print("start")
	init()
	load_obj_ims()
	search_fail=0
	game_rounds=0
	#begin_watch()

	while True:
		gm=get_gm()
		height,width=gm.img.shape[:2]
		print("*",end="");sys.stdout.flush()
		try:
			res=simple_CU()
			if res:
				print(res)
				search_fail=0
				if res=="gaojiyanxi":
					game_rounds+=1
					if game_rounds%5==0:mail_to_me("summary","rounds = %d"%game_rounds,gm.img)
			else:
				search_fail+=1
			if search_fail>1 and search_fail%100==0:
				mail_to_me('Error提醒',"search_fail>100")
				if search_fail>1000:
					#end_watch()
					sys.exit()
		except Exception as e:
			print(e)
			print("Error")
			traceback.print_exc()
			try:
				mail_to_me("Program Error",str(traceback.format_exc())+str(e))
			except Exception as e2:
				pass
			time.sleep(600)
		time.sleep(1.5)
		
	#end_watch()	

def test_begin_game():
	'''test main process'''
	global gm,stx,sty,height,width
	
	logging.info('start')
	init()
	# while True:
		# do_situertedexiaoyan()
	do_map({'road_fleet':'fleet2','boss_fleet':'fleet1'})	
	#begin_watch()
	#do_meiritiaozhan()
	#do_kunnan('8-2')
	#do_yanxi()
	#do_putong('10-2')	
	#end_watch()
	logging.info('end')
	
if __name__=="__main__":
	# begin_game()
	test_begin_game()