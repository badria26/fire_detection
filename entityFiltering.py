import csv

class EntityDocument:
		
	def csv_writer(self,data,path):
		with open(path, "a") as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(data)
