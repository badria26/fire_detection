import cv2
import numpy as np
from filter_model import FilteringModel
import Tkinter as tk
from PIL import Image,ImageTk


class ColorFiltering(object):
	def __init__(self,*args):
		
		self.modelFilter = FilteringModel()		
		global lower,upper
		lower=[]
		upper=[]
		
	def bgr2rgb(self,imageBGR):
		return cv2.cvtColor(imageBGR,cv2.COLOR_BGR2RGB)
		
	def rgb2hsv(self,imageRGB):
		return cv2.cvtColor(imageRGB,cv2.COLOR_BGR2HSV)
		
	def displayinTk(self,image,imgLabel):
		img = Image.fromarray(image).resize((320,240),Image.ANTIALIAS)
		imgTk=ImageTk.PhotoImage(image=img)
		imgLabel.configure(image=imgTk)
		imgLabel.image=imgTk
		imgLabel._image_cache= imgTk
		
	def setUpper(self,high_h,high_s,high_v):
		global upper
		upper=[] 		
		upper=['{}'.format(high_h.get()),
					'{}'.format(high_s.get()),
					'{}'.format(high_v.get())]
					
		#print "upper value are:{0}".format(upper)
	
	def setLower(self,low_h,low_s,low_v):
		global lower
		lower=[]
		
		lower=['{}'.format(low_h.get()),
					'{}'.format(low_s.get()),
					'{}'.format(low_v.get())]		
		#print "lower value are:{0}".format(lower)
			
	def getUpper(self):
		#upper= map(int,upper)
		return upper
	def getLower(self):
		#lower= map(int, lower)
		return lower 
	
	def filterMask(self,image,lower,upper):	
		#lower= self.getLower()
		#upper=self.getUpper()
		if type(lower)!=int and type(upper)!=int:
			
			lower= map(int,lower)
			upper=map(int,upper)
			
		lower=np.array(lower)
		upper=np.array(upper)
		
		#print '{},{}'.format(lower,upper)
		'''
		lower= np.array(self.FilteringModel.getLower())
		upper= np.array(self.FilteringModel.getUpper())
		'''
		mask=cv2.inRange(image, lower, upper)
		#ret,mask=cv2.threshold(image,250,255,cv2.THRESH_BINARY)
		
		#print mask[10:15,25:30]
		return mask
		
		'''
		TclError: expected floating-point number but got ".1884278736.1880385976.1880420440"
'''
