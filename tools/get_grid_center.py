#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random,copy
import numpy as np
from matplotlib import pyplot as plt
from skimage import io,feature,morphology,filters,color,measure
import queue,time

def debugim(im):
	imm=np.asarray(im)
	io.imshow(imm)
	plt.show()

	
# def bfs(st,co):
	# global edges,floodfill3,height,width,vis,sumtime
	


	# Q.put(st)



def get_grid_center(im):
	global edges,floodfill3,height,width,vis,sumtime

	im=im.copy()
	
	height=im.shape[0];width=im.shape[1]

	im=color.rgb2gray(im)
	edges = feature.canny(im, sigma=0.5)
	vis=np.zeros((height,width),dtype=np.bool)
	totc=0
	floodfill3=np.empty((height,width),dtype=np.int32)
	floodfill3[:]=-1
	dire=((-1,0),(1,0),(0,-1),(0,1))
	Q=queue.Queue()
	sumtime=0
	for i in range(height):
		for j in range(width):
			if(not vis[i,j]):
				sttime=time.time()
				Q.queue.clear()
				Q.put((i,j))
				while(not Q.empty()):
					x,y=Q.get()
					if(edges[x-1:x+2,y-1:y+2].sum()>0):continue
					else:
						floodfill3[x-1:x+2,y-1:y+2]=totc
					for d in range(4):
						nx,ny=(x+dire[d][0],y+dire[d][1])
						if(nx<=0 or nx>=height-1 or ny<=0 or ny>=width-1 or vis[nx,ny]):continue
						vis[nx,ny]=True
						Q.put((nx,ny))
				sumtime+=time.time()-sttime
				totc+=1
	print(sumtime)
	
	coid_cnt=np.zeros(totc,dtype=np.int32)
	coid_center=np.zeros((totc,2),dtype=np.int32)
	coid_bound=np.zeros((totc,4),dtype=np.int32)
	coid_bound[:,0]=10000 ; coid_bound[:,1]=0 ; coid_bound[:,2]=10000 ; coid_bound[:,3]=0
	for i in range(height):
		for j in range(width):
			if(floodfill3[i,j]!=-1):
				coid_id=floodfill3[i,j]
				coid_cnt[coid_id]+=1
				coid_center[coid_id]+=[i,j]
				coid_bound[coid_id,0]=min(coid_bound[coid_id,0],i)
				coid_bound[coid_id,1]=max(coid_bound[coid_id,1],i)
				coid_bound[coid_id,2]=min(coid_bound[coid_id,2],j)
				coid_bound[coid_id,3]=max(coid_bound[coid_id,3],j)

	for i in range(totc):
		piece_h=abs(coid_bound[i,0]-coid_bound[i,1])+1
		piece_w=abs(coid_bound[i,2]-coid_bound[i,3])+1
		if piece_h/piece_w>2 or piece_h/piece_w<0.5:coid_cnt[i]=0

	for i in range(totc):
		if(coid_cnt[i]==0):continue
		# coid_center[i][0]/=coid_cnt[i]
		# coid_center[i][1]/=coid_cnt[i]
		coid_center[i]=[(coid_bound[i,0]+coid_bound[i,1])//2,(coid_bound[i,2]+coid_bound[i,3])//2]
		
	coid_color=255*np.random.random((totc,3))
	coid_color=coid_color.astype(np.uint8)
	imflood=np.zeros((height,width,3),dtype=np.uint8)

	# for i in range(height):
		# for j in range(width):
			# if(floodfill3[i,j]==-1):imflood[i,j]=[255,255,255]
			# else: imflood[i,j]=coid_color[floodfill3[i,j]].copy()

	center_list=[]
	for i in range(totc):
		if(1500<=coid_cnt[i]<=10000):
			center_list.append((coid_center[i][0],coid_center[i][1]))


	center_list.sort()
	center_number=len(center_list)
	center_matrilis=[]
	las=0
	for i in range(center_number):
		if i==center_number-1 or abs(center_list[i][0]-center_list[i+1][0])>10:
			if(i-las<=0):las=i+1;continue
			center_matrilis.append(center_list[las:i+1])
			las=i+1
	for row in center_matrilis:
		row.sort(key=lambda x:x[1])
	grid_h=len(center_matrilis)
	center_row_dislis=[100000]*len(center_matrilis)
	for i in range(len(center_matrilis)):
		row=center_matrilis[i]
		for j in range(len(row)-1):
			if(abs(center_row_dislis[i]-(row[j+1][1]-row[j][1]))<20):
				center_row_dislis[i]=(center_row_dislis[i]+row[j+1][1]-row[j][1])/2
			else:
				center_row_dislis[i]=min(center_row_dislis[i],row[j+1][1]-row[j][1])
	for i in range(len(center_matrilis)):
		row=center_matrilis[i]
		for j in range(len(row)-1):
			tmp=int(round((row[j+1][1]-row[j][1])/center_row_dislis[i]))
			center_row_dislis[i]=(center_row_dislis[i]+(row[j+1][1]-row[j][1])/tmp)/2
				
		
	center_leftside=[]
	for i in range(grid_h):
		center_leftside.append(center_matrilis[i][0])

	flag=True
	while(flag):
		flag=False
		rest=len(center_leftside)
		lr_x=np.zeros(rest)
		lr_y=np.zeros(rest)
		for i in range(rest):
			lr_x[i],lr_y[i]=center_leftside[i][0],center_leftside[i][1]
		lr_b=(np.dot(lr_x,lr_y)-rest*lr_x.mean()*lr_y.mean())/(np.dot(lr_x,lr_x)-rest*lr_x.mean()**2)
		lr_a=lr_y.mean()-lr_b*lr_x.mean()
		
		errdis=0
		errid=-1
		for i in range(rest):
			tmperr=center_leftside[i][1]-(lr_a+lr_b*center_leftside[i][0])
			tmperr=abs(tmperr)+tmperr//2
			if tmperr>errdis:
				errdis=tmperr
				errid=i
		if errdis>20:
			del center_leftside[errid]
			flag=True

	center_lucorner=(center_matrilis[0][0][0],lr_a+lr_b*center_matrilis[0][0][0])
	center_row_xlis=[]
	for i in range(grid_h):
		center_row_xlis.append(center_matrilis[i][0][0])

	i=0
	while i<grid_h-1:
		if i+2<=grid_h-1:
			if (center_row_xlis[i+2]-center_row_xlis[i+1])*1.6<=(center_row_xlis[i+1]-center_row_xlis[i]):
				center_row_xlis.insert(i+1,center_row_xlis[i]+(center_row_xlis[i+2]-center_row_xlis[i+1]))
				center_row_dislis.insert(i+1,center_row_dislis[i]+(center_row_dislis[i+2]-center_row_dislis[i+1]))
				center_matrilis.insert(i+1,[])
				grid_h+=1
		elif i>=1:
			if (center_row_xlis[i]-center_row_xlis[i-1])*1.6<=(center_row_xlis[i+1]-center_row_xlis[i]):
				center_row_xlis.insert(i+1,center_row_xlis[i]+(center_row_xlis[i]-center_row_xlis[i-1]))
				center_row_dislis.insert(i+1,center_row_dislis[i]+(center_row_dislis[i]-center_row_dislis[i-1]))
				center_matrilis.insert(i+1,[])
				grid_h+=1
		i+=1

	center_row_st=[]
	for i in range(grid_h):
		center_row_st.append(lr_a+lr_b*center_row_xlis[i])

	grid_w=0
	for i in range(len(center_matrilis)):
		if(len(center_matrilis[i])>0):
			grid_w=max(grid_w,int(round((center_matrilis[i][-1][1]-center_row_st[i])/center_row_dislis[i]))+1)


	center_rightside=np.zeros((grid_h,2))
	for i in range(grid_h):
		center_rightside[i]=((center_row_xlis[i],center_row_st[i]+(grid_w-1)*center_row_dislis[i]))

	flag=True
	while(flag):
		flag=False
		rest=len(center_rightside)
		lr_x=center_rightside[:,0].reshape(rest)
		lr_y=center_rightside[:,1].reshape(rest)
		lr_b=(np.dot(lr_x,lr_y)-rest*lr_x.mean()*lr_y.mean())/(np.dot(lr_x,lr_x)-rest*lr_x.mean()**2)
		lr_a=lr_y.mean()-lr_b*lr_x.mean()
		
		errdis=0
		errid=-1
		for i in range(rest):
			tmperr=center_rightside[i][1]-(lr_a+lr_b*center_rightside[i][0])
			tmperr=abs(tmperr)-tmperr//2
			if tmperr>errdis:
				errdis=tmperr
				errid=i
		if errdis>10:
			center_rightside=np.delete(center_rightside,errid,0)
			flag=True

	for i in range(grid_h):
		center_row_dislis[i]=(lr_a+lr_b*center_row_xlis[i]-center_row_st[i])/(grid_w-1)

	grid_center=np.zeros((grid_h,grid_w,2),dtype=np.int32)
	for i in range(grid_h):
		for j in range(grid_w):
			grid_center[i,j]=(int(center_row_xlis[i]),int(center_row_st[i]+j*center_row_dislis[i]))
	
	return grid_center

	# imgrid=np.zeros((height,width,3),dtype=np.uint8)
	# for i in range(grid_h):
		# for j in range(grid_w):
			# imgrid[grid_center[i][j][0]-1:grid_center[i][j][0]+2,grid_center[i][j][1]-1:grid_center[i][j][1]+2]=[255,255,255]
			# imflood[grid_center[i][j][0]-1:grid_center[i][j][0]+2,grid_center[i][j][1]-1:grid_center[i][j][1]+2]=[0,0,0]

