#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random,copy
import numpy as np
from skimage import io,feature,morphology,filters,color,measure

grid_data={
"3-4":{
"hill":[(0,5),(0,6),(0,7),(1,6),(1,7),(2,0)],
"supply":[(1,5)]
}
}

def load_grid_data(grid_status,map_name):
	for objname,lis in grid_data[map_name].items():
		for pos in lis:
			grid_status[pos]=objname
