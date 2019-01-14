#!/usr/bin/env python

import Tkinter as tk
from tkFileDialog import askopenfilename,askdirectory
import os
import cv2
import tkMessageBox as msg
import timeit,time
from PIL import Image,ImageTk
import numpy as np
import csv
import sys
import threading
from motion_controller import MotionSub
from motion_model import MotionModel
import draw_controller
from filter_controller import ColorFiltering
from path_controller import ControllerPath
from entityFiltering import EntityDocument

class MainForm(tk.Tk):
	def __init__(self):
		
		tk.Tk.__init__(self)
		container = tk.Frame(self)
		container.pack(side="top", fill="both",expand=True,anchor="center")
		container.grid_rowconfigure(0,weight=1)
		container.grid_columnconfigure(0,weight=1)
		#tk.Frame.__init__(self,parent)
		container.tkraise()
		
		#manggil kelas
		#self.controller = controller
		self.controlPath = ControllerPath()
		self.controlMotion = MotionSub()
		self.controlFiltering =ColorFiltering()
		self.toCSV = EntityDocument()
		self.modelMotion=MotionModel()
		
		#header
		self.header= tk.Label(self,text="Pendeteksian Api Menggunakan Citra NIRGB dan Background Substraction \n",font=("Cambria",12,"bold")).place(x=300,y=20) 

		#btn load 
		self.btnLoad=tk.Button(self,text="Load Video",command=self.window_show)
		self.btnLoad.place(x=0,y=40)
		
		#btn save
		self.saveBtn = tk.Button(self,text="save value",command=self.saveVal,state="disabled")
		self.saveBtn.place(x=50,y=400 )
		
		#frame preview		
		framePreview= tk.LabelFrame(self,text="Preview")
		framePreview.place(x=430,y=60,width=400,height=600)
		#image 
		self.image_ori_lbl = tk.Label(self,text='Original', image=None)
		self.image_ori_lbl.place(x=450, y=80)
		
		self.hsv_image_lbl = tk.Label(self,text="HSV", image=None)
		self.hsv_image_lbl.place(x=450, y=380)
		
		self.stopEvent=None
		self.thread=None
		#variabel text inputan alpha dan treshold value
		self.entryA=tk.StringVar()
		self.entryT=tk.StringVar()
	
		#tampilan scrollbar		
		self.Hmin=tk.IntVar()
		self.Hmax=tk.IntVar()
		self.Smin=tk.IntVar()
		self.Smax=tk.IntVar()
		self.Vmin=tk.IntVar()
		self.Vmax=tk.IntVar()
        
		self.labelHue = tk.Label(self,text='Hue', width=7, height=2)
		self.labelHue.place(x=0, y=80)
		self.low_hue = tk.Scale(self,label='Low', from_=0, to=179, length=200, showvalue=2, orient=tk.HORIZONTAL,variable=self.Hmin,command=self.updateImage)
		self.low_hue.place(x=0, y=100)
		self.high_hue = tk.Scale(self,label='High',from_=0, to=179, length=200, orient=tk.HORIZONTAL,variable = self.Hmax,command=self.updateImage)
		self.high_hue.place(x=200, y=100)
		self.high_hue.set(179)

		self.labelS = tk.Label(self, text='Saturation', width=10, height=2)
		self.labelS.place(x=0, y=180)
		self.low_sat = tk.Scale(self, label='Low', from_=0, to=255, length=200, orient=tk.HORIZONTAL,variable=self.Smin, command=self.updateImage)
		self.low_sat.place(x=0, y=200)
		self.high_sat = tk.Scale(self, label="High",from_=0, to=255, length=200, orient=tk.HORIZONTAL,variable=self.Smax,command=self.updateImage)
		self.high_sat.place(x=200, y=200)
		self.high_sat.set(255)

		self.labelV = tk.Label(self, text='Value', width=7, height=2)
		self.labelV.place(x=0, y=275)
		self.low_val = tk.Scale(self, label="Low",from_=0, to=255, length=200, orient=tk.HORIZONTAL,variable=self.Vmin,command=self.updateImage)
		self.low_val.place(x=0, y=300)
		self.high_val = tk.Scale(self, label="High",from_=0, to=255, length=200, orient=tk.HORIZONTAL,variable=self.Vmax,command=self.updateImage)
		self.high_val.place(x=200, y=300)
		self.high_val.set(255)
		
		#set text
		self.textFile=tk.Text(self,wrap="word",height=10,width=50,font=("Times New Roman",12),spacing1=1)
		self.textFile.place(x=850,y=270)
		#set param
		lblFrame= tk.LabelFrame(self,text="Set Parameter").place(x=850,y=115,width=220,height=100)
		self.info = tk.Label(self,text="batas inputan 0.0 - 1.0").place (x=855,y=130)
		self.lblAlpha= tk.Label(self,text="Learning Rate").place(x=855,y=150)
		self.entryalpha=tk.Entry(self,width=5,textvariable=self.entryA).place(x=950,y=150)
		
		self.lblThresh = tk.Label(self,text="Threshold").place(x=855,y=180)
		self.entryThresh=tk.Entry(self,width=5,textvariable=self.entryT).place(x=950,y=180)
		
		self.btnProc=tk.Button(self,text="Analyze",activebackground="white",command=self.analyzeMotion,state="disabled")
		self.btnProc.place(x=850,y=240)
		
		#Threading to run method running()
		self.stopEvent =threading.Event()
		self.thread=threading.Thread(target=self.analyzeMotion,args=())
		self.thread.start()
	def window_show(self):
		#untuk menampilkan hasil prosesing filtering warna ke tkinter
		global filename
				
		path= self.controlPath.askFile()	
		
		ext=os.path.splitext(path)[1]
		if ext != ".avi":
			msg.showinfo(title="Info",message="make sure your file is .avi extension")	
			return 0
		self.controlPath.setPath(path)
		filename = self.controlPath.getPath()
		#self.controlMotion.setPath(path)
		#filename= self.controlMotion.getPath()
		self.cap=cv2.VideoCapture(filename)
		print filename

		if filename != '':			
			#self.cap=cv2.VideoCapture(filename)
			self.Hmin.set(self.Hmin.get())
			self.Hmin.set(self.Hmin.get())
		else:
			print "No Selected Image"
			return 0
			
		#variable to motion
		self.textFile.insert(1.0,'filename: %s \n'%(filename))
		self.cap=cv2.VideoCapture(filename)
		
		#get frame rate dan total frame
		self.frame_rate=self.modelMotion.getFrameRate(self.cap)
		self.total_frame=self.modelMotion.getTotalFrame(self.cap)
		
		#show the result to GUI
		self.textFile.insert(2.0,'frame rate =%d \n'%(self.frame_rate))
		self.textFile.insert(3.0,'total frame =%d \n'%(self.total_frame))
		#self.controlFilter.displayinTk(rgbPre,self.labelImg)
		
		self.saveBtn['state']='normal'
		self.btnProc['state']='normal'
		#controller
	def updateImage(self,*args):		
		
		#read video dan menampilkan video agar dpaat berulang di Tkinter maka digunakan fungsi after.
		#coba proses baca video inputan dan menampilkan di tkinter
		self.mulai = time.time()
		#get nilai HSV dari trackbar
		self.controlFiltering.setLower(self.Hmin,self.Smin,self.Vmin)
		self.controlFiltering.setUpper(self.Hmax,self.Smax,self.Vmax)		
	
		#get Image	
		
		self.cap.set(1,1)		
		ret,img=self.cap.read()		
		
		if img is None:
			msg.showinfo(title="Info",message="last frame reach")
			#return 0
		#get image
		#self.img_ori =cv2.resize(img,(10,10),interpolation= cv2.INTER_AREA)
		self.img_ori = img
		self.img_hsv= self.img_ori.copy()
		#print self.img_ori[10:15,25:30,0] #blue
		#print self.img_ori[10:15,25:30,1] #green
		#print self.img_ori[10:15,25:30,2] #red
		
		#konversi warna 
		rgb= self.controlFiltering.bgr2rgb(self.img_ori)
		hsv = self.controlFiltering.rgb2hsv(self.img_hsv)
		
		#print hsv[10:15,25:30,0] #hue
		#print hsv[10:15,25:30,1] #sat
		#print hsv[10:15,25:30,2] #val
		
		#display in tkinter
		self.controlFiltering.displayinTk(rgb,self.image_ori_lbl)

		#define range color
		lower= self.controlFiltering.getLower()
		upper= self.controlFiltering.getUpper()
		self.mask= self.controlFiltering.filterMask(hsv,lower,upper)
		#print mask [10:15,25:30]	
		
		#convert to tkinter format
		self.controlFiltering.displayinTk(self.mask,self.hsv_image_lbl)

		return self.mask

	def saveVal(self):
		'''fungsi ini untuk menyimpan nilai trackabr value dr filtering pada mask,
		nilai bisa digunakan untuk pelatihan naive bayes'''
		
		self.controlFiltering.setLower(self.Hmin,self.Smin,self.Vmin)
		self.controlFiltering.setUpper(self.Hmax,self.Smax,self.Vmax)
		isi=[
			"{}".format(self.controlPath.getPath()),
			'{}'.format(self.Hmin.get()),
			'{}'.format(self.Hmax.get()),
			'{}'.format(self.Smin.get()),
			'{}'.format(self.Smax.get()),
			'{}'.format(self.Vmin.get()),
			'{}'.format(self.Vmax.get())]
		
		#save ke dalam file .csv
		self.controlPath.save2csv(isi)
		
		self.end=time.time()
		print "execution time: %2f ms"%(self.end-self.mulai)
	
		
	def analyzeMotion(self):
		global Toplevel
		self.start =timeit.default_timer()
		
		#untuk entry nilai learning rate(alpha)
		self.alpha=float(self.entryA.get())
		#untuk entri nilai threshold
		self.thresh=float(self.entryT.get())
	
		#get path from controller		
		self.pathname=self.controlPath.getPath()	
		self.cap=cv2.VideoCapture(self.pathname)
		
		#get the lower and upper mask of video
		self.minVal=self.controlFiltering.getLower()
		self.maxVal = self.controlFiltering.getUpper()
		
		#new window untuk menampilkan video 
		board=tk.Toplevel()
		imgLabel=tk.Label(master=board)
		imgLabel.pack()
		roiLabel=tk.Label(master=board)
		roiLabel.pack()
		
		self.controlMotion.running(self.pathname,board,self.alpha,self.thresh,self.minVal,self.maxVal,imgLabel,self.mask,self.cap,roiLabel)
		
		elapsed=timeit.default_timer()-self.start
		#print "time run :%.2f s"%elapsed
		self.resFolder=self.modelMotion.setFolderDest(self.pathname)
		
		
		self.textFile.insert(6.0,'analyze video...Done\n')
		self.textFile.insert(7.0,'result at {}\n'.format(self.resFolder))
		
		board.after(0,func=lambda:self.analyzeMotion)
		board.title("Motion Analysis Preview")
		board.mainloop()
	

if __name__ == "__main__":

	#app=tk.Tk()
	app=MainForm()
	app.title("Tugas Akhir 2 - Badria Riswanda")
	app.geometry("1500x900")
	app.mainloop()

 
#ganti openImage ke video dengan toplevel -
#video berhasil di-play di form Filter(14 november)
#next applying trackbar (ganbatte~) berhasil(27 november)
#next save value trackbar (done)
#dictionary, terlalu random.unorder akan bingung untuk disimpan  ke dalam csv (failed)
#videoberhasil terbca namun cepat berhemti . error: di cvtColor opencv 3 (solved)


#23 maret 2018
#tampilin video di gui ke dalan sistem
#27 maret 2018
#coba gunakan Threading untuk menampilkan video di tkinter dan opencv
#1 april 2018
#label berjalan di Toplevel, tapi hanya sampai 1 frame, butuh diulang lagi dengan fungsi after atau update()

#filename berubah jadi None ketika dterapkan MVC
#16 april 
#alhamdulillahhhhh.........berhasil muncul videonya di Tkinter
'''cari solusi : 
6.trackbar muncul ketika video di load, jika belum mka state='disabled' (error)
7. menampilkan video dengan thread

16/7/2018
8. PERUBAHAN -> tampilkan perubahan saat trackbar digeser --> berhasil 16/7
9. cari mengamil frame pertama dari video

erro;
File "mainPage.py", line 216, in window_show
    self.low_hue.set(self.low_hue.get()+1)
AttributeError: 'int' object has no attribute 'set'

#hitung ulang tiap proses , keluarkan nilainy
#pelajari lagi konsepnya
'''
