#!/usr/bin/env python
#encoding: utf-8 #para acentos 


import sys  
import design  
import os  

import threading
import serial

from PyQt4 import *

from PyQt4.QtGui import *

from PyQt4.QtCore import *



import locale
import time


PortData = "/dev/ttyUSB0"


class SetGraphic(QtGui.QMainWindow, design.Ui_MainWindow):
	
	def __init__(self):
		
		super(self.__class__, self).__init__()
		self.setupUi(self)
		self.setWindowTitle("Nayax QT Raspberry")

		self.Data_RX = ""
		self.MoneyInMDB = 0.00

		def start_Read_RX_1():
			self.MyThread1.start()
			self.plainTextEdit.setPlainText("Insert coin")

		def start_Read_RX_2():
			self.MyThread1.start()
			self.plainTextEdit.setPlainText("Swipe your card")

		def timeout1():
			try:
				self.MyThread1.start()
				self.MyTimer1.stop()
				print "thread Start"
			except:
				print "error thread"

		
		def Rrecive_Data(Data_RX):
			self.Data_RX = Data_RX
			self.MoneyInMDB = 0
			array = [ ]
			wordLed=len(self.Data_RX)
			for i in range(0,wordLed/2):
				array.append(self.Data_RX[i*2] + self.Data_RX[(i*2)+1])
			
			if((wordLed/2)>=9) :
				if((array[0]=='f2')and(array[1]=='a1')and(array[7]=='f3')):

					self.MoneyInMDB = float (((int(array[2]) - 30) * 100) + ((int(array[3]) - 30) * 10) + (int(array[4]) - 30) + (int(str(array[5]),16) * 0.5))
					
					if self.MoneyInMDB >= 5:
						self.PayCashBtn.Init_Hardware()#Disable MDB
						self.plainTextEdit.setPlainText("Vend success")

				elif((array[0]=='f2')and(array[1]=='fa')and(array[7]=='f3')):
				
					self.plainTextEdit.setPlainText("Cancel request")
				
				elif((array[0]=='f2')and(array[1]=='fb')and(array[7]=='f3')):
				
					self.plainTextEdit.setPlainText("Vend denied")
				
				elif((array[0]=='f2')and(array[1]=='fc')and(array[7]=='f3')):
				
					self.plainTextEdit.setPlainText("Session denied")
				
				elif((array[0]=='f2')and(array[1]=='fd')and(array[7]=='f3')):
				
					self.plainTextEdit.setPlainText("Cancelled")
				
				elif((array[0]=='f2')and(array[1]=='fe')and(array[7]=='f3')):
				
					self.plainTextEdit.setPlainText("vend success")
				
				elif((array[0]=='f2')and(array[1]=='ff')and(array[7]=='f3')):
				
					self.plainTextEdit.setPlainText("Empty")
			
			self.MoneyInMDB = locale.currency(self.MoneyInMDB, grouping=True)
			self.label_2.setText(str(self.MoneyInMDB))
			print "print RX " + str(self.MoneyInMDB)
			self.MyTimer1.start()


		self.PayCashBtn = MyThread_Pay_Cash_Card()
		self.PayCashBtn.Init_Hardware()
		
		self.pushButton.clicked.connect(self.PayCashBtn.CashCommand)
		self.pushButton.clicked.connect(start_Read_RX_1)
		
		self.pushButton_2.clicked.connect(self.PayCashBtn.CardCommand)
		self.pushButton_2.clicked.connect(start_Read_RX_2)
		
		self.MyThread1 = MyThread_RX()
		self.MyThread1.MySignal1_RX.connect(Rrecive_Data)

		self.MyTimer1 = QTimer()
		self.MyTimer1.timeout.connect(timeout1)


	def __del__(self):
		self.MyTimer1.stop()
		self.MyThread1.terminate()



class MyThread_RX(QThread):
	
	MySignal1_RX = pyqtSignal(str)

	def __init__(self):
		QThread.__init__(self)

	def __del__(self):
		self.wait()
	
	def run(self):
		print "try to read port"
		ser = serial.Serial(PortData, 115200)
		msg = ser.read(9).encode('hex')
		if msg:
			try:
				self.MySignal1_RX.emit(str(msg))
				print('return data port ' + msg)
			except ValueError:
				print('Wrong data')
		else:
			pass
		ser.close()


class MyThread_Pay_Cash_Card(QThread):

	def __init__(self):
		QThread.__init__(self)

	def __del__(self):
		self.wait()


	def Init_Hardware(self):
		data = "Init Hardware"
		print data
		ser = serial.Serial(PortData, 115200)
		CMD_MDB_DISABLE = '\x02\xf0\x00\x00\x03\xf3'
		ser.write(CMD_MDB_DISABLE)
		ser.close()
	
	def CashCommand(self):
		data = "Pay Cash"
		print data
		ser = serial.Serial(PortData, 115200)
		CMD_MDB_ENABLE = '\x02\xf1\x00\x00\x03\xf4'
		ser.write(CMD_MDB_ENABLE)
		ser.close()

	def CardCommand(self):
		data = "Pay Card"
		print data
		ser = serial.Serial(PortData, 115200)
		CMD_MDB_DISABLE = '\x02\xf0\x00\x00\x03\xf3'
		ser.write(CMD_MDB_DISABLE)
		time.sleep(0.5)
		CMD_MDB_NAYAX = '\x02\x00\x00\x0A\x03\x0d'
		ser.write(CMD_MDB_NAYAX)
		ser.close()


def main():

	app = QtGui.QApplication(sys.argv)
	form = SetGraphic()  
	form.show()
	app.exec_()  # and execute the app

if __name__ == '__main__':  # if we're running file directly and not importing it
	main() # run the main function
