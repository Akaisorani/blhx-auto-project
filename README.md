# blhx-auto-project

还是不太work，给SIFT加了RANSAC发现还是有个问题不能很好解决：
* 对尺寸较小的物体(<40*40pix)不能很好的判定存在不存在，因为特征点会比较少，比较难卡，这个问题在地图里面最突出

## 说明
* 主程序是blhx.py
* 如果用的不是夜神模拟器，需要到tools/wintools.py里改一下get_window_pos下面的clsname和title，让程序可以找到你的模拟器窗口
* 怎么找你的clsname和title？运行模拟器，运行一下wintools.py，然后从显示的列表里面找

## 环境

* python3
* windows
* opencv
* ~~skimage~~
