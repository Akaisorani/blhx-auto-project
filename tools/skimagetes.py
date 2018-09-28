#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import numpy as np
import queue
from skimage.io import imread,imshow,imsave
from skimage import feature,morphology,filter
from matplotlib import pyplot as plt
import win32api,win32con,win32gui

# print(help(imread))
img=imread('map_sample.png',as_grey=True)

def similar(co1,co2,simstd):
	return sum([abs(int(co1[i])-int(co2[i])) for i in range(3)])<255*3*simstd

def bfs(pos,simstd):
	global vis,dire
	if(vis[pos[0]][pos[1]]):return
	
	Q=queue.Queue()
	Q.put(pos)
	while(not Q.empty()):
		pos=Q.get()
		if(vis[pos[0]][pos[1]]):continue
		# print(pos)
		vis[pos[0]][pos[1]]=True
		boundflag=False
		for d in range(4):
			nd=(pos[0]+dire[d][0],pos[1]+dire[d][1])
			if(nd[0]<0 or nd[0]>=hight or nd[1]<0 or nd[1]>=width or vis[nd[0]][nd[1]]):continue
			if(similar(img[pos[0]][pos[1]],img[nd[0]][nd[1]],simstd)):
				Q.put(nd)
			else:
				boundflag=True
		if(boundflag):img[pos[0]][pos[1]]=[255,255,0,255]
		
	
def depar(img,simstd):
	global vis,dire
	vis=[([0]*width) for i in range(hight)]
	dire=((-1,0),(1,0),(0,-1),(0,1))
	
	for i in range(hight):
		for j in range(width):
			bfs((i,j),simstd)


print(img[0][0],img[0][1],img[0][0]+img[0][1])
print(img.shape)
hight=img.shape[0]
width=img.shape[1]


# depar(img,0.07)
# edges = feature.canny(img, sigma=0.5)

imshow(edges)
plt.show()





# win32api.MessageBox(win32con.NULL,'hello world!','fuck you!',win32con.MB_OK)


