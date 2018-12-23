import numpy as np
import cv2
				
class Object_detect(object):
	def __init__(self):
		self.ratio=0.85
		self.MIN_MATCH_COUNT=5
		self.sift = cv2.xfeatures2d.SIFT_create()
		self.index_params = dict(algorithm = 0, trees = 5)	# FLANN_INDEX_KDTREE = 0
		self.search_params = dict(checks=50)   # or pass empty dictionary
		self.flann = cv2.FlannBasedMatcher(self.index_params, self.search_params)
		self.debug_flag=False
		
	def pre_detect(self,obj):
		obj.kp, obj.des=self.sift.detectAndCompute(obj.img, None)
		return obj.kp, obj.des
	
	def show_img(self,img):
		cv2.imshow('kp',img)
		cv2.waitKey(100000)
		cv2.destroyAllWindows()				
	
	def show_keypoints(self,img,kp):
		img=cv2.drawKeypoints(img,kp,None)
		self.show_img(img)

	def show_matches(self,img1,kp1,img2,kp2,matches,**kw_args):
		img_with_matches = cv2.drawMatches(img1, kp1, img2, kp2, matches, None, flags=2, **kw_args)
		self.show_img(img_with_matches)
	
	def sift_detect(self, obj1, obj2):

		# find the keypoints and descriptors with SIFT
		kp1, des1 = (obj1.kp, obj1.des) if obj1.kp is not None else self.pre_detect(obj1)
		kp2, des2 = (obj2.kp, obj2.des) if obj2.kp is not None else self.pre_detect(obj2)
		
		# Show keyPoints in each picture
		if self.debug_flag:
			self.show_keypoints(obj1.img,kp1)
			self.show_keypoints(obj2.img,kp2)
		
		# Use knn match where k=2
		matches = self.flann.knnMatch(des1,des2,k=2)
		
		# Apply ratio test
		good_matches=[]
		for m1, m2 in matches:
			if m1.distance < self.ratio * m2.distance:
				good_matches.append(m1)
		
		# show matches
		if self.debug_flag:
			if good_matches:
				print('(good num / kp1 num) = (%d / %d) = %.2f'%(len(good_matches),len(kp1),len(good_matches)/len(kp1)))
				self.show_matches(obj1.img,kp1,obj2.img,kp2,good_matches)
			else:
				print("no good matches")
		
		if len(good_matches)<self.MIN_MATCH_COUNT: return None, 0
		#if not (len(good_matches)>=len(kp1)//3): return None, len(good_matches)/len(kp1)
		
		queryPoss = np.float32([ kp1[m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
		trainPoss = np.float32([ kp2[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)
		
		transMat, mask = cv2.findHomography(queryPoss, trainPoss, cv2.RANSAC,5.0)
		matchesMask = mask.ravel().tolist()
		
		# check whether there is enough matched points
		if sum(matchesMask)<4 or sum(matchesMask)/len(kp1)<0.3: return None, sum(matchesMask)/len(kp1)
		
		# 映射中心
		height1, width1 = obj1.img.shape[:2]
		src_center_pos = np.float32([width1/2,height1/2]).reshape(-1,1,2)
		dst_center_pos = cv2.perspectiveTransform(src_center_pos,transMat) # 转化中心
		dst_center_pos_tuple=tuple(np.squeeze(np.int32(dst_center_pos),(0,1)).tolist())
		# show matches and position
		if self.debug_flag:
			# 映射边框
			src_edge_poss = np.float32([ [0,0],[0,height1-1],[width1-1,height1-1],[width1-1,0] ]).reshape(-1,1,2)
			dst_edge_poss = cv2.perspectiveTransform(src_edge_poss,transMat) # 转化边框
			img2 = cv2.polylines(obj2.img,[np.int32(dst_edge_poss)],True,255,3, cv2.LINE_AA)
			
			img2 = cv2.circle(img2,dst_center_pos_tuple,5,(0,0,255),-1,cv2.LINE_AA)
			
			self.show_matches(obj1.img,kp1,obj2.img,kp2,good_matches,matchesMask=matchesMask)
		
		return (dst_center_pos_tuple[1],dst_center_pos_tuple[0]), sum(matchesMask)/len(kp1)	
		
if __name__=='__main__':
	class Obj(object):
		def __init__(self,img,kp=None,des=None):
			self.img=img
			self.kp=kp
			self.des=des
			
	def remove_alpha(img):
		if len(img.shape)==3 and img.shape[2]==4:
			return np.delete(img,3,2)
		else:
			return img
	obj_dect=Object_detect()			
	obj_dect.debug_flag=True
	from skimage import io
	img1=cv2.imread('./../res/enemy_dd.PNG')
	img1=remove_alpha(img1)
	img2=cv2.imread('train.PNG')
	img2=remove_alpha(img2)
	print('shape',img1.shape,img2.shape)
	obj1=Obj(img1)
	obj2=Obj(img2)
	
	
	obj_dect.pre_detect(obj1)
	obj_dect.pre_detect(obj2)
	pos,score=obj_dect.sift_detect(obj1,obj2)
	print(pos,score)