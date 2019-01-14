#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import cv2
import shutil
#from motion_controller import MotionSub

class MotionModel():
	def __init__(self):
		#self.controlMotion=MotionSub
		self.pathname=[]
		self.alpha=[]
		self.thresh=[]
		
	def getFrameRate(self,cap):
		self.frame_rate=cap.get(5)
		return self.frame_rate

	def getTotalFrame(self,cap):
		self.total_frames=cap.get(7)
		return self.total_frames
	
	def setPath(self,pathname):
		self.pathname=str(pathname)
		
	def getPath(self):
		return self.pathname
		
	def getAlpha(self,var):
		#self.alpha=float(var.get())
		return float(self.alpha.get())
		
	def getThresh(self,thresh):
		self.thresh=float(thresh.get())
		return self.thresh
		
	def setAlpha(self,alpha):
		self.alpha=alpha
		
	def setThresh(self,thresh):
		self.thresh=thresh
		
	def setFolderDest(self,pathname):
		self.pathname=pathname
		self.folder_dest= "hasilUji"
		
		norm_path= os.path.normpath(self.pathname)
		(filepath, filename)=os.path.split(norm_path)
		(shortname,ext)=os.path.splitext(filename)
		_,folDest= os.path.split(filepath)
				
		#directory for final result
		self.file_dest=os.path.join(self.folder_dest,shortname)
		return self.file_dest
	
	def getNameofFile(self):
		#get name of setFolderDest
		files=[]
		if os.path.exists(self.file_dest):
			for (dirpath,dirname,filenames) in walk(self.file_dest):
				(shortname,ext)=os.path.splitext(filenames)
				files.extend(shortname)
			return 0
			
		return files
		
	def writeToFile(self,pathname,curFrame,frameId):
		'''this method to save the result to the selected folder'''
		self.pathname=pathname
		#set folder destination
		#self.file_dest= self.modelMotion.setFolderDest(self.pathname)
		self.file_dest= self.setFolderDest(self.pathname)
		if not os.path.exists(self.file_dest):
			os.makedirs(self.file_dest)
		#else:
			#shutil.rmtree(self.file_dest)
			#os.makedirs(self.file_dest)
		#write detected image here
		cv2.imwrite(self.file_dest + "/"+str(frameId)+".jpg",curFrame)
		return self.file_dest
		
	def count_files(self):
		
		dirs='home/pi/coding/fire_detect/hasilUji'
		count = len([name for name in os.listdir(dirs) if os.path.isfile(os.path.join(dirs,name))])
		
		return files

def main():
	
	return 0

if __name__ == '__main__':
	main()


#error: NameError: global name 'alpha' is not defined

