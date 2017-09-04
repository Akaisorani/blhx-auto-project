#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random,copy
import numpy as np
from skimage import io,feature,morphology,filters,color,measure

def get_grid_status(grid_center,obj_pos):
	grid_status=np.zeros((grid_center.shape[0],grid_center.shape[1]),dtype='<U32')
	for obj_name,lis in obj_pos.items():
		for pos in lis:
			mindis=1000000000;
			x,y=-1,-1
			for i in range(grid_center.shape[0]):
				for j in range(grid_center.shape[1]):
					if((grid_center[i,j][0]-pos[0])**2+(grid_center[i,j][1]-pos[1])**2<mindis):
						mindis=(grid_center[i,j][0]-pos[0])**2+(grid_center[i,j][1]-pos[1])**2
						x,y=i,j
			if (x,y)!=(-1,-1):
				grid_status[x,y]=obj_name
	# pos=np.where(grid_status=="self_armor")
	# grid_status[pos[0][0],pos[1][0]]=''
	# grid_status[pos[0][0]+2,pos[1][0]]="self"
	
	return grid_status
