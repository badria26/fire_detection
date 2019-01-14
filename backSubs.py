import cv2
import numpy as np
import time
from scipy import sum, average

#backsub consist of two main steps;
#1.background initialization
#2.background update
class Background:
	def __init__(self,alpha,firstFrame,threshVal):
		#initiliase construcntor
		self.alpha=alpha
		self.backgroundStatic=firstFrame 
		self.threshVal=threshVal
		self.usingOpencv = True
		self.accAvg = 0.95	#to accumulatedWeight
		self.iteration = 1	#to iteration in morphology
		
	def medianBlur(self,frame,filter_size):
	#pre processing image menggunakna mediaan Blur
		#return cv2.medianBlur(frame,5)
		
		temp=[]
		frame=np.array(frame)
		counter=filter_size//2
		window=[
			(i,j)
			for i in range(-counter,filter_size-counter)  #window width
			for j in range(-counter,filter_size-counter)	#window height
		]
		index= len(window)//2
		for i in range(len(frame)):
			for j in range(len(frame[0])):
				frame[i][j]=sorted(0 if(
										min(i+a,j+b)<0 or len(frame)<=i+a or len(frame[0])<=j+b
										) 
									else frame[i+a][j+b]
									for a,b in window
								)[index]
		return frame
	
		
	def gaussianBlur(self,frame):
		#pre-processing image using gaussianBlur
		return cv2.GaussianBlur(frame,(5,5),0)
		
	def denoise(self,frame):
		#use median blur
		frame=self.medianBlur(frame,5) #cv2.medianBlur(frame,5)
		#use gaussian blur (src,ksize,sigmax,gmaY)
		frame=self.gaussianBlur(frame) #cv2.GaussianBlur(frame,(5,5),0)
		
		return frame
		
	def toGrayscale(self,img):
		# if image array in 3D change to 2D
		if len(img.shape)==3:
			return average(img,-1)
		else:
			return img
			
	def normalize(self,img):
		#to set 0,1
		rang = img.max() - img.min()
		if rang==0:
			rang=1
		rang_min = img.min()
		return (img-rang_min)*255/rang
		
		
	def absoluteDiff(self,img1, img2):
		#this method to set background update of video using absolute different
		#set image to 0,1 value
		img1 =self.normalize(img1) # np.asarray(img1,dtype=np.uint8) 
		img2 =self.normalize(img2) # np.asarray(img2,dtype=np.uint8) 
		#calculate difference and norm
		abs_diff = abs(img1-img2)
		abs_diff = (abs_diff*255).astype("uint8")
		#print abs_diff		
		
		return abs_diff
		
	def setBackground(self,srcImage):
		#self.background = np.float32(srcImg)
		self.color_img = srcImage.copy()
		cv2.accumulateWeighted(self.color_img,self.backgroundStatic,self.accAvg)
		self.staticBackground = cv2.convertScaleAbs(self.backgroundStatic)
		return self.staticBackground
		
	def getForeground(self,frame):
		#start = time.clock()
		
		#denoise image
		frame= self.gaussianBlur(frame)
		self.backgroundModel=self.gaussianBlur(self.backgroundStatic)
		
		#static background
		#self.backgroundModel= self.setBackground(frame)
		#set backgroundn to grayscale value
		frame = self.toGrayscale(frame)
		self.backgroundModel= self.toGrayscale(self.backgroundModel)
		#print frame[10:15,25:30]
		#print self.backgroundModel[10:15,25:30]
		#aply backround averaging formula to update the background
		#new_background=current_frame*learning rate+old_background*(1-learningn rate)
		self.backgroundModel=frame*self.alpha+self.backgroundModel*(1-self.alpha)
		self.backgroundModel = cv2.convertScaleAbs(self.backgroundModel)
		
		#FIND FOREGROUND
		if self.usingOpencv is True: 
			self.foreground= cv2.absdiff(self.backgroundModel.astype(np.uint8),frame)
		else:
			self.foreground = self.absoluteDiff(self.backgroundModel.astype(np.uint8),frame)
			
		#print self.foreground[10:15,25:30]
		#set to grayscale img
		#self.grayImg=cv2.cvtColor(self.foreground,cv2.COLOR_BGR2GRAY)
		#threshold image to get black and white
		ret,self.grayImg=cv2.threshold(self.foreground,self.threshVal,255,cv2.THRESH_BINARY)
		#print self.grayImg[10:15,25:30]
		#erode to remove noise, clean up raw mask
		#dilate areas to merge bounded objects
		#open=dilate(erode(img)) (cleandiff) 
		#closed =erode(dilate)= dirtydiff
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
		self.grayImg= cv2.morphologyEx(self.grayImg,cv2.MORPH_OPEN,kernel,self.iteration)
		self.grayImg= cv2.morphologyEx(self.grayImg,cv2.MORPH_CLOSE,kernel,self.iteration)
		return self.grayImg
		
		
		#the higher number iteration the more erosion take place in opening before dilation in closing.
		#set minimum contours
		
'''
problem to solve;
di line 28
ValueError: operands could not be broadcast together with shapes (240,320,3) (52,37,3) 
	tidak bisa melakukan operasi pada image yg berbeda ukuran matriksnya. 
	1.cari cara agar dapat di proses meski beda matriks
	2. ubah ukuran agar masing-masing dapat diproses, frame = selectedRoi(52,37,3), backgroundModel= frame asli video(240,320,3)
solved: diubah frame sama nilainya dengan inputan 

1 mei2018
line 29: ValueError :The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
tidak memenuhi kondisi boolean

28 mei 2018
instal modul scipy

29 mei
OpenCV Error: Assertion failed (depth == CV_8U || depth == CV_16U || depth == CV_32F) in cvtColor, file /home/pi/opencv-3.1.0/modules/imgproc/src/color.cpp, line 7935
/home/pi/opencv-3.1.0/modules/imgproc/src/color.cpp:7935: error: (-215) depth == CV_8U || depth == CV_16U || depth == CV_32F in function cvtColor
-> ubah ke bentuk yug bisa diolah oleh cvtcolor = [0,255]

30 mei, jika menggunakan method line 100,muncul error. 
src is not a numpy array, neither a scalar
berhasil jika menggunakan cv2.absdiff

31 mei
sudah bisa menggunakan absoluteDiff() tp akurasiny rendah.

17 september 
absdiff buatan sendiri dengan cv2.absDiff() opencv menunjukkan hasil yg berbeda. 
coba ditelusuri lagi sebabnya.
#18 Sept 
#morpholig closed emmbuat banyak deteksi yg salah

'''		


