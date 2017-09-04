import os
import random
import win32api,win32con,win32gui
import time

def get_mouse_pos():
	x,y=win32api.GetCursorPos()
	return x,y

def mouse_move(pos,delay=None):
	win32api.SetCursorPos(pos)
	if delay!=None: time.sleep(delay)
		
def mouse_click(pos=None,delay=None):
	if pos!=None: mouse_move(pos)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
	if delay!=None: time.sleep(delay)

def mouse_drag(spos,tpos,delay=None):
	mouse_move(spos)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
	time.sleep(0.1)
	timeseg=(abs(spos[0]-tpos[0])+abs(spos[1]-tpos[1]))/100/1000
	for i in range(1,101):
		mpos=(int((spos[0]*(100-i)+tpos[0]*i)/100),int((spos[1]*(100-i)+tpos[1]*i)/100))
		mouse_move(mpos,timeseg)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)	
	if delay!=None: time.sleep(delay)

def messagebox(message,title="notice"):
	win32api.MessageBox(win32con.NULL,message,title,win32con.MB_OK)
	
def get_window_pos():
	clsname='Qt5QWindowIcon'
	title='夜神模拟器'
	hWnd=win32gui.FindWindow(clsname,title)
	if hWnd==0:return ((-1,-1),(-1,-1))
	rec=win32gui.GetWindowRect(hWnd)
	lefttop=rec[0:2]
	rightbottom=rec[2:4]
	return (lefttop,rightbottom)
	
def show_window_attr(hWnd):
	if not hWnd:return
	clsname=win32gui.GetClassName(hWnd)
	title=win32gui.GetWindowText(hWnd)
	print((hWnd,clsname,title))
	
def enum_windows():
	hWndList=[]
	win32gui.EnumWindows(lambda hWnd,param:param.append(hWnd),hWndList)
	for h in hWndList:
		show_window_attr(h)

if __name__=="__main__":
	messagebox("work")