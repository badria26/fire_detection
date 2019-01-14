#import cv2
#import Tkinter as tk
from tkFileDialog import askopenfilename,askdirectory
from tkMessageBox import askquestion,showinfo
from entityFiltering import EntityDocument
from filter_controller import ColorFiltering

###########################################33
#			CONTROLLER
##############################################
class ControllerPath:
	def __init__(self,*args, **kwargs):
		self.frame_seq= True
		self.images = False
		
		self.fileValue = EntityDocument()
		self.controlFiltering= ColorFiltering()
		
	def askFile(self):
		self.answer=askquestion('choose file','Input Video ?')
		if self.answer=='yes':
			
			self.pathname=askopenfilename()
			
		else :
			
			self.pathname=askdirectory()
		
		return self.pathname
		
			
	def setPath(self,pathname):
		self.pathname=str(pathname)
		
	def getPath(self):
		return self.pathname
		
	def save2csv(self,data):
		pathFile='/home/pi/coding/fire_detect/nilai_HSV.csv'
		#save ke dalam file .csv
		try:
			fileValue= self.fileValue.csv_writer(data,pathFile)
			showinfo(title="Succes",message="File Berhasil disimpan di %s"%pathFile)
		except Exception as e:
			print e
		return fileValue
	
	
