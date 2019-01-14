import csv
import os
from init import FormFilter #GUI filter page

class SaveValue():
	def __init__(self,hsv,filecsv):
		self.hsv=hsv
		self.filecsv = filecsv
		
class SaveValController():
	'''creates objek of model,manipulating atribut, mengirim perintah ke view 
	
	'''
	def __init__(self):
		
		self.data = ValueModel()
		self.formFilter = FormFilter(self,controller)
		
	def saveValue(self):
		data= []
		Hmin=self.formFilter.Hmin.get()
		Hmax=self.formFilter.Hmax.get()
		Smin= self.formFilter.Smin.get()
		Smax=self.formFilter.Smax.get()
		Vmin=self.formFilter.Vmin.get()
		Vmax=self.formFilter.Vmax.get()
		
		input_=(str("%d,%d,%d,%d,%d,%d"%(Hmin,Hmax,Smin,Smax,Vmin,Vmax)))
		data.append(input_)
		self.data.setData(data)
		
		with open("save_value.csv","a") as f:
			writer=csv.writer(f)
			writer.writerows(data)
			
	def getValue(self):
		""" Function doc """
		return self.data.getData()
		
	
	def setval (self,hsv):
		""" check if list empty- """
		hsv={}
		if not hsv:
			print "dict is empty"
		'''if empty, then set the value to the list'''
		self.setValue()
		
class ValueModel:
	def __init__(self, *args,**kwargs):
		self.data = []
		self.value={}
		
	def setData(self,data):
		self.data=data
		
	def getData (self):
		""" Function doc """
		return self.data
		
	def setValue(self,value):
		self.value=value
		
	def getValue(self):
		return value 
		
		
		
