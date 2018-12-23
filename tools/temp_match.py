import numpy as np
import cv2

# SIFT
sift = cv2.xfeatures2d.SIFT_create()
# FLANN parameters
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks=50)   # or pass empty dictionary
flann = cv2.FlannBasedMatcher(index_params,search_params)

debug_flag=False

class Obj(object):
	def __init__(self,img,kp=None,des=None):
		self.img=img
		self.kp=kp
		self.des=des


def pre_detect(obj):
	obj.kp, obj.des=sift.detectAndCompute(obj.img, None)

def filter_match_result(queryPos,trainPos,diag):
	while trainPos.any():
		trainCenter=np.mean(trainPos,axis=0,dtype=np.int32)
		c=trainPos-np.tile(trainCenter,(trainPos.shape[0],1))
		c=(c[:,0]**2+c[:,1]**2)**0.5
		if not (c>diag).any():break
		id=np.argmax(c)
		trainPos=np.delete(trainPos,id,0)
		queryPos=np.delete(queryPos,id,0)
	
	return queryPos,trainPos
				
def sift_detect(obj1, obj2):

	# find the keypoints and descriptors with SIFT
	kp1, des1 = obj1.kp, obj1.des
	kp2, des2 = obj2.kp, obj2.des
	
	if debug_flag:
		# Show keyPoints in each picture
		obj1.img=cv2.drawKeypoints(obj1.img,kp1,obj1.img)
		cv2.imshow('kpp',obj1.img)
		cv2.waitKey(100000)
		cv2.destroyAllWindows()
		obj2.img=cv2.drawKeypoints(obj2.img,kp2,obj2.img)
		cv2.imshow('kpp2',obj2.img)
		cv2.waitKey(100000)
		cv2.destroyAllWindows()	
	
	matches = flann.knnMatch(des1,des2,k=2)
	# Apply ratio test
	good = [m for m, n in matches if m.distance < 0.6 * n.distance]
	
	if debug_flag:
		if good:
			# cv2.drawMatchesKnn expects list of lists as matches.
			print('good num',len(good))
			print('len kp1',len(kp1))
			goodfordraw=[[x] for x in good]
			img3 = cv2.drawMatchesKnn(obj1.img, kp1, obj2.img, kp2, goodfordraw, None, flags=2)
			cv2.imshow('mch_res',img3)
			cv2.waitKey(100000)
			cv2.destroyAllWindows()
			pass
		else:
			print("no good")
	
	if not good: return None, 0
	if not (len(good)>=len(kp1)//3): return None, len(good)/len(kp1)
	
	queryPos=np.array([kp1[mkp.queryIdx].pt for mkp in good],dtype=np.int32)
	trainPos=np.array([kp2[mkp.trainIdx].pt for mkp in good],dtype=np.int32)
	
	diag=(obj1.img.shape[0]**2+obj1.img.shape[1]**2)**0.5
	queryPos,trainPos=filter_match_result(queryPos,trainPos,diag)
	
	queryCenter=np.mean(queryPos,axis=0,dtype=np.int32)
	trainCenter=np.mean(trainPos,axis=0,dtype=np.int32)
	return (trainCenter[1],trainCenter[0]), len(good)/len(kp1)
	#return bgr_rgb(img3)

if __name__=='__main__':
	debug_flag=True
	img1=cv2.imread('t1.jpg')
	if len(img1.shape)==3 and img1.shape[2]==4:img1=np.delete(img1,3,2)
	img2=cv2.imread('t2.jpg')
	if len(img2.shape)==3 and img2.shape[2]==4:img2=np.delete(img2,3,2)
	print('shape',img1.shape,img2.shape)
	obj1=Obj(img1)
	obj2=Obj(img2)
	pre_detect(obj1)
	pre_detect(obj2)
	pos,score=sift_detect(obj1,obj2)
	print(pos,score)