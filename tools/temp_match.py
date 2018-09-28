import numpy as np
import cv2

# SURF
surf = cv2.xfeatures2d.SURF_create()
# FLANN parameters
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks=50)   # or pass empty dictionary
flann = cv2.FlannBasedMatcher(index_params,search_params)

class Obj(object):
	def __init__(self,img,kp=None,des=None):
		self.img=img
		self.kp=kp
		self.des=des


def pre_detect(obj):
	obj.kp, obj.des=surf.detectAndCompute(obj.img, None)


def surf_detect(obj1, obj2):

	# find the keypoints and descriptors with SURF
	kp1, des1 = obj1.kp, obj1.des
	kp2, des2 = obj2.kp, obj2.des
	matches = flann.knnMatch(des1,des2,k=2)
	# Apply ratio test
	good = [m for m, n in matches if m.distance < 0.4 * n.distance]
	if not good or len(good)<3: return None, -1
	# cv2.drawMatchesKnn expects list of lists as matches.
	goodfordraw=[[x] for x in good]
	img3 = cv2.drawMatchesKnn(obj1.img, kp1, obj2.img, kp2, goodfordraw, None, flags=2)
	# cv2.imshow('mch_res',img3)
	# cv2.waitKey(600)
	# cv2.destroyAllWindows()
	
	queryPos=np.array([kp1[mkp.queryIdx].pt for mkp in good],dtype=np.int32)
	trainPos=np.array([kp2[mkp.trainIdx].pt for mkp in good],dtype=np.int32)
	queryCenter=np.mean(queryPos,axis=0,dtype=np.int32)
	trainCenter=np.mean(trainPos,axis=0,dtype=np.int32)
	return (trainCenter[1],trainCenter[0]), len(good)
	#return bgr_rgb(img3)

if __name__=='__main__':
	from skimage import io
	img1=io.imread('t1.png')
	if len(img1.shape)==3 and img1.shape[2]==4:img1=np.delete(img1,3,2)
	img2=io.imread('t2.png')
	print(img1.shape,img2.shape)
	obj1=Obj(img1)
	obj2=Obj(img2)
	pre_detect(obj1)
	pre_detect(obj2)
	surf_detect(obj1,obj2)