#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random,copy
from PIL import ImageGrab,Image
import numpy as np
from matplotlib import pyplot as plt
from skimage import io,feature,morphology,filters,color,measure
# import pytesseract
import win32api,win32con,win32gui
# import ctypes
import queue,time
from wintools import *

def debugim(im):
	imm=np.asarray(im)
	io.imshow(imm)
	plt.show()

raise "zhenglikuozhan"
# time.sleep(2)
# print("start")
# win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
# time.sleep(0.05)
# win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
# print("end")

# print(time.time()-sttime)
# debugim(im2)
# debugim(im)