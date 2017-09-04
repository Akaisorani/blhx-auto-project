#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random,copy
import numpy as np
from skimage import io,feature,morphology,filters,color,measure

def drawrec(im,x,y,h,w):
	for i in range(x,x+h):
		im[i,y]=(255,0,0,255)
		im[i,y+w]=(255,0,0,255)
	for j in range(y,y+w):
		im[x,j]=(255,0,0,255)
		im[x+h,j]=(255,0,0,255)
		
def mergepoi(lis):
	global match_result
	for i in range(len(lis)-1):
		if lis[i][0]==-1:continue
		for j in range(i+1,len(lis)):
			if lis[j][0]==-1 or lis[i][0]==-1 or np.dot(lis[i]-lis[j],lis[i]-lis[j])>100:continue
			if(match_result[lis[i][0],lis[i][1]]>match_result[lis[j][0],lis[j][1]]):
				lis[j][0]=-1
			else:
				lis[i][0]=-1
	newlis=[]
	for pos in lis:
		if pos[0]!=-1:newlis.append(pos)
	newlis.sort(key=lambda x:match_result[(x[0],x[1])],reverse=True)
	return np.array(newlis)

def get_obj_pos(im,im_objs):
	global match_result
	ret=dict()
	for name,im_obj in im_objs.items():
		match_result=feature.match_template(im,im_obj)
		# ij=np.unravel_index(np.argmax(match_result),match_result.shape)
		# ijlis=filterarr(match_result,lambda x:x>0.8)
		ijlis=np.where(match_result>0.6)
		ijlis=np.dstack((ijlis[0],ijlis[1]))[0]
		ijlis=mergepoi(ijlis)
		# print(ijlis)
		# print([match_result[(ij[0],ij[1])] for ij in ijlis])
		if len(ijlis)!=0:
			ijlis[:,0]+=im_obj.shape[0]//2;ijlis[:,1]+=im_obj.shape[1]//2
			if name=='self' : ijlis[0]+=[int(im.shape[0]*0.2),-int(im.shape[1]*0.0311)]
		ret[name]=ijlis
		# for ij in ijlis:
			# drawrec(im_match_test,ij[0],ij[1],enum_enemy.shape[0],enum_enemy.shape[1])
	return ret
