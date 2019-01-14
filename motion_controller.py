#!/usr/bin/env python

import cv2
import numpy as np
import Tkinter as tk
from tkFileDialog import askopenfilename,askdirectory
from tkMessageBox import askquestion,showinfo
import os,glob
from PIL import Image,ImageFilter,ImageTk
import time,timeit
import draw_controller
import backSubs
from ast import literal_eval
from datetime import datetime, timedelta
import csv
import math
from motion_model import MotionModel
from filter_controller import ColorFiltering
from path_controller import ControllerPath
from entityFiltering import EntityDocument

class MotionSub():
	def __init__(self):
		
		self.modelMotion=MotionModel()
		self.controlFilter=  ColorFiltering()
		self.controlPath= ControllerPath()
		self.entityDocument = EntityDocument()
		
		self.listFile=[]
		self.folder = "result_dir"
		self.burnin=0
		self.scan=0
		self.frame_rate=0
		self.def_area='draw'
		self.setROI =False
		self.includedROI =None
		self.set_areaCounter=False
		self.fileDest=" "
		self.play=False
		#folder destination
		self.folder_dest="hasilUji"
		self.file_dest=''
		
		self.saveVid="both"
		
		self.minVal=[]
		self.maxVal=[]
		self.path_time= "/home/pi/coding/fire_detect/nilai_HSV.csv"
		
	def askFile(self):
		self.answer=askquestion('choose file','Input Video ?')
		if self.answer=='yes':
			self.frame_seq = True
			self.pathname=askopenfilename()
			
		else :
			self.frame_seq =False
			self.pathname=askdirectory()
			self.images=True
		
		return self.pathname		
	
	def readVids(self):
		'''
		method ini digunakan unutk melakukan ekstraksi terhadap video yang kemungkinan 
		akan diolah di proses filtering dan motion apabila menggunakan 
		image sequence
		'''
		#method to get input from user
		
		self.askFile()
		os.mkdir(self.folder)
		cap = cv2.VideoCapture(self.pathname)
		#cap.set(cv2.CAP_PROP_POS_MSEC,5000) #Skip to 5s
		self.count=0
		while True:
			#start reading frame
			ret,frame=cap.read()
			if not ret:
				break
			#set the name of image
			names=os.path.join(self.folder,"img%d.jpg"%self.count)
			cv2.imwrite(names,frame)
			self.listFile.append(names)
			self.count+=1
		return self.listFile
		
	def preProc(self,lblImg):
		'''
		this method provide to recognizing input file, set ROI for processing image
		set learning rate, threshold value,initiliaze background'''
		#set stamp lidt
		self.stamp=[]
		
		#write header row for stamp 
		self.stamp.append(("Time","Frame",'Position'))
		
		#capture output for area detectiom
		self.result_img=[]
		
		#capture output
		self.frameHasil=0
		
		##No contours, there was not enough motion compared to background, did not meet threshold
		self.noCountr=0
		
		#capture minimumbox size for plotting
		self.avg_box=[]
		
		#Empty list for area counter
		self.areaCounter=[]
		self.areaCounter.append(("Time","Frame","X","Y"))
		
		#to set draw ROI
		self.top = 0
		self.bottom = 1
		self.left = 0
		self.right = 1
		
		#flag on
		self.noMotion=False
		
		#label Image
		self.labelImg=lblImg
		
		#################################
		#Begin video capture
		#################################
		
		
		#if self.frame_seq is False means using video
		if self.frame_seq:
			
			ext=os.path.splitext(self.pathname)[1]
			
			#get from video capture
			self.cap=cv2.VideoCapture(self.pathname)
			
			
			#get global frame rate
			self.frame_rate=round(self.cap.get(5))
			#make sure extension is .avi
			if ext in ['.avi','.AVI']:
				#self.frame_rate=1
				print "frame rate set to 1"
			else: 
				showinfo(title="Info",message="make sure your file is .avi extension")
				return 0				
			#get frame related to time of begin video
			self.frame_time=self.cap.get(0)
			
			#get total number of frame
			self.total_frames=self.cap.get(7)
			#skip x frame according to user input
			for x in range(1,int(float(self.burnin)*int(self.frame_rate)*60)):
				self.cap.grab()
			
			#set frame skip counter 
			self.frameSkip=0
			
			#get the lower and upper mask of video
			self.low=self.controlFilter.getLower()
			self.up= self.controlFilter.getUpper()
			print '{0}-{1}'.format(self.low,self.up)
			
			#capture the first image
			self.cap.set(1,1)
			ret,firstImage=self.cap.read()
			#if not read
			if not ret:
				raise ValueError("no file image capture")
			#convert background to be like mask filtering 
			rgbImg= self.controlFilter.bgr2rgb(firstImage)
			hsvImg= self.controlFilter.rgb2hsv(rgbImg)
				
			firstImage= self.controlFilter.filterMask(hsvImg,self.low,self.up)
							
			print "begin motion detection"
		else:
			#self.frame_sequence is True using image sequence
			self.cap = cv2.VideoCapture(self.pathname)
			#begin read file image sequence
			image_ext=["*.jpg","*.jpeg","*.png"]
			pathImg = [os.path.join(self.pathname,x) for x in image_ext]
			self.jpgs=[]
			for extension in pathImg:
				ketemu=glob.glob(extension)
				self.jpgs.extend(ketemu)
			print ("banyaknya image di folder : %d"% len(self.jpgs))
			
			#set the first image as initialize background
			firstImage= cv2.imread(self.jpgs[0])
			#convert to gray Img
			#self.showImg=cv2.cvtColor(firstImage,cv2.COLOR_BGR2GRAY)
			self.total_frames=len(self.jpgs)
			self.frame_rate=1
		
		#make copy for markup
		imageCopy= firstImage.copy()
		
		#self.includeRoi = raw_input(str("include ROI?"))
		#set ROI
		if self.setROI:
			self.selectedRoi=draw_controller.Udef(imageCopy,"Region of Interest")
			self.selectedRoi=self.selectedRoi[-4:]
			if len(self.selectedRoi)==0:
				raise ValueError('Error:please select an area to be ROI')
			if self.includedROI=="include":
				print "cropping frame...complete"
				self.showImg = firstImage[self.selectedRoi[1]:self.selectedRoi[1]+self.selectedRoi[3],self.selectedRoi[0]:self.selectedRoi[0]+self.selectedRoi[2]]
				print self.showImg.shape[0:2]
			else:
				firstImage[self.selectedRoi[1]:self.selectedRoi[3],self.selectedRoi[0]:self.selectedRoi[2]]=255
				self.showImg=firstImage
		else:
			self.showImg=firstImage
			

		#show image
		if self.setROI:			
			cv2.imshow("ROI area",self.showImg)
			#cv2.imshow("user self area",self.cropImg)
			cv2.waitKey(5)
			cv2.destroyAllWindows()
		
		self.controlFilter.displayinTk(self.showImg,self.labelImg)
		
		self.width=np.size(self.showImg,1)
		self.height=np.size(self.showImg,0)
		frameSize=(self.width,self.height)
		print frameSize
		
		return self.showImg
	#=======================================#
	#compute background selama video looping
	#=======================================#
	
	
	def running(self,pathname,board,alpha,thresh,minVal,maxVal,imgLabel,mask,cap,roiLabel):
		
		self.mask = mask
		self.learningRate=alpha
		self.threshVal=thresh
		self.cap=cap
		
		start=time.time()
		self.images=False
	   
		self.minVal=minVal
		self.maxVal = maxVal
		
		self.pathname= pathname
		self.times=[]
	
		self.backgroundInit=backSubs.Background(self.learningRate,self.mask,self.threshVal)
		#print self.backgroundInit[10:15,25:30]
		#hitung jumlah frames
		self.frame_total=0
		self.total_frames=0
		
		
		try:
			#read video input
			ret,oriFrame=self.cap.read()
			if not ret:
				print '=========last frame  reach======='
				
				return 0
			#convert current frame to be like mask filtering
			rgbImg_cf = self.controlFilter.bgr2rgb(oriFrame)				
			hsvImg_cf=self.controlFilter.rgb2hsv(rgbImg_cf)
			
			#put mask filtering image  here
			currentFrame= self.controlFilter.filterMask(hsvImg_cf,self.minVal,self.maxVal)
								
			#if not the last frame, scan frames
			if not self.scan==0:
				if self.noMotion:
					for x in range(1,self.scan):
						if not self.images:
							self.cap.grab()
						else:
							oriFrame=jpgs.pop()
							self.frame_total=self.frame_count+1
				else:
					print "theres no motion in video"
					return 0
			else:				
				#dibuat pass karena self.scan !=0 maka terbaca dan dilanjutkan k proses slnjutnya
				pass
				
			#capture from video
			if self.images is False:
				#skip read frame every n second
				frameId=int(round(self.cap.get(1))) #current frame per second
				t_frame=int(self.cap.get(0)/1000) #current time fo frame
	
				#print "frame %d detik ke-%d" %(frameId,t_frame)
			else:
				currentFrame=cv2.imread(self.jpgs.pop())
				for count,item in enumerate(self.jpgs):
					print 'frame ke-{0}'.format(count)
					
			self.frame_total +=1				
			#frame_t0=time.time()
			#============================#
			#background substraction
			#============================#
			#self.start = time.time()
			#do background substraction here-> foreground identification
			grayImg=self.backgroundInit.getForeground(currentFrame)
			#print grayImg[10:15,25:30]
			 
			#if set Roi, subset the image
			if self.setROI:
				if self.includedROI =="include":
					mask=np.ones(grayImg.shape,np.bool)
					mask[self.selectedRoi[1]:self.selectedRoi[1]+self.selectedRoi[3],self.selectedRoi[0]:self.selectedRoi[0]+self.selectedRoi[2]]=False
					grayImg[mask]=0
				else:
					mask= cv2.bitwise_and(currentFrame,currentFrame, mask=grayImg)
					grayImg[mask]=0
			
			#==========================#
			#contour analysis and post procesing
			#==========================#
			coords= []
			bbox_list=[]
			counter=[]
			
			#Empty list for position stamp
			stamp_position=[] 
			
			imgCopy=grayImg.copy()
			#calculate white pixel as motion data
			_,contours,_=cv2.findContours(imgCopy,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
			length = len(contours)
			maxArea= -1			
			i = 0 
			
			# define minimum area Rect and minimum Enclosing circle
			for c in contours:
				
				#get bounding Rect				
				rect=cv2.boundingRect(c)
				#set contour smaller 
				if rect[2]<50 or rect[3]<50:
					continue
				point = rect
				#print "{0}x{1} + {2}x{3}".format(point[0],point[1],point[2],point[3])
				self.setRoi(point[0],point[1],point[2],point[3],rgbImg_cf)
				#get minimum area rect
				#rect=cv2.minAreaRect(c)
				#box=cv2.boxPoints(rect)
				#print type(box)
				
				#convert all coord floating point to int
				#box=np.int0(box)
								
				#write to file frame has detected contour
				self.modelMotion.writeToFile(self.pathname,rgbImg_cf,frameId)
			#contours for 
			imgContour=cv2.drawContours(imgCopy,contours,-1,(255,0,0),1) 
			
			#display in Tkinter format
			self.controlFilter.displayinTk(rgbImg_cf,imgLabel)
			self.controlFilter.displayinTk(imgCopy,roiLabel)
			
			board.after(100,func=lambda:self.running(pathname,board,alpha,thresh,minVal,maxVal,imgLabel,mask,self.cap,roiLabel))			
			#set for time
			
			
		except Exception, e:
			print str(e)
		
		end=time.time()-start
		
		self.times=["alpha: %.4f, frame %d detik ke-%d, lama:%.2f s"%(self.learningRate,frameId,t_frame,end)]			
		self.entityDocument.csv_writer(self.times,self.path_time)
		#print "time elapsed: %.2f s"%(end)
		
	def rotatedRect(self,img,contour):
		self.contour=contour
		rect=cv2.minAreaRect(self.contour)
		box=cv2.boxPoints(rect)
		box=np.int0(box)
		return cv2.drawContours(img,[box],0,(0,0,255),2)
	
	def setRoi(self,x,y,w,h,image):
		#get bounding Rect
		#return cv2.rectangle(image,(x+30,y+30),(x+w-50,y+h-30),(0,255,0),2)
		return cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
		
		
	def makeVid(self):
		#method ini untuk membuat video berdasarkan class motion 
		if self.saveVid not in ("video","both"): return ("no video output")
		
		#get file input dan output  
		#normpath= to normalize pathname ex: s//b,a/b/,a/foo/.../b -> a/b                       
		#normcase()=normalize case of a pathname on unix&macOs X-> path unchanged, case sensitive->lowercase, /->\
		norm_path= os.path.normpath(self.pathname)
		(filepath, filename)=os.path.split(norm_path)
		(shortname,ext)=os.path.splitext(filename)
		(_,folDest)= os.path.split(filepath)
		
		#name the output folder from the output destination
		self.file_dest=os.path.join(self.folder_dest,shortname)
		
		if self.fileDest==' ':
			#viDest=os.path.join(filepath,shortname,shortname+'.avi')
			viDest=os.path.join(self.file_dest,shortname+'.avi')	
		else:
			viDest=os.path.join(self.fileDest,shortname,shortname+'.avi')
			
		print "video output will be at %s"%(viDest)
		
		#jika folder belum ada maka buat folder baru
		#if not os.path.exists(self.file_dest):
		os.makedirs(self.file_dest)
			
		#find all jpegs
		jpgs=glob.glob(os.path.join(self.file_dest,"*.jpg"))
		
		#get frame rate and size of image
		if not self.images:
			self.cap = cv2.VideoCapture(self.pathname)
			
			#if not self.frame_seq:
			if self.frame_seq:
				fr=round(self.cap.get(5))
			else:
				fr=self.frame_rate
				
			orig_img=self.cap.read()[1]
			
		#get info about camera and img
		width=np.size(orig_img,1)
		height=np.size(orig_img,0)
		frame_size=(width, height)
		
		#define codec
		fourcc=self.cap.get(6)
		#create video writer object
		
		out=cv2.VideoWriter(viDest,cv2.VideoWriter_fourcc('M','J','P','G'),float(fr),frame_size)
				
		if not len(jpgs) == 0:
			#split and sort jpgs name
			jpgs.sort(key=draw_controller.getint) 
			try:
				#loop through image and write frame to video
				for f in jpgs:
					cf=cv2.imread(f)
					out.write(cf)
				#release if finished	
				self.cap.release()
				out.release()
			except Exception as e:
				print(str(e))
				pass
		else:
			print "Theres nothing frame saved"
			pass
		
		#if only video, delete the frames video
		if self.saveVid=="video":
			for f in jpgs:
				os.remove(f)
				
	def postProcessing(self):
		
		#report to csv file, time and area stamp
		frameReport = self.folder_dest+"/"+"Frames.csv"
		isi=[]
		for data in self.modelMotion.getNameofFile():
			isi.append(data)
		self.entityDocument.csv_writer(isi,frameReport)
		
		#with open(frameReport,'wb') as f:
			#writer=csv.writer(f)
			#writer.writerows(self.modelMotion.getNameofFile())
		
		#if self.set_areaCounter:
			#areaReport=self.folder_dest+"/"+"AreaCounter.csv"
			
			#with open(areaReport,'wb') as f:
				#writer=csv.writer(f)
				#writer.writerows(self.areaCounter)
				
		#############################
		#Run analysis pool video
		#=============================
		
		#print "total frame yg terhitung: %s"%self.frame_total
				
		##count time dimulai dari backSub dilakukan
		#self.end=time.time()-self.start
		#print "time exec: %f s"%(self.end)
		
		
				
'''
void = MotionSub()
	
#void.readVids()
#print void.listFile
void.preProc()
void.running()
void.makeVid()
void.postProcessing()
'''

#Note to Programmer
#3 maret
#berhasil write video
#fail to input informasi stamp di csv

#untuk menambah akurasi, tmbahkan shadow removal
#cv2.rect masih belum berhasil-->done

#17 Juli
#Perubahan!!!! mask filtering jadi input di video currentFrame, hasil trckbar jadi inputan filterMask()
#setlower dan upper apply di fiteringMask()

#8 septmber
#ubah ke method method, sesuaikan dengan sequence diagram
#11 septmber masih belum bisa menyimpan image yg memiliki hasil deteksi-->done
#16 september belum bisa menghitung file terdeteksi di dalam folder
#25 oktober tambahakan stamp for point detection and stamp for time, see MotionMeerkat-> MotionClass.py




