#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 12:37:17 2018
@author: alex

Характериограф, измеряет ВАХ

Вход: Umin, Umax, Imax, nPoints, COM
Выход: файл с двумя столбцами (U, I), график
"""
import sys
sys.setdefaultencoding('utf-8')

import os
import numpy as np
import pylab as plt
import serial
import time

class GPD73303():
	# общий функционал
	def __init__(self, port, timeout=1):
		if not (port is None):
			self.openPort(port, timeout)
	def __del__(self):
		self.closePort()
	def closePort(self):
		print('[*] Закрываю порт '+ self.ser.name + '..')
		self.ser.close()
	def openPort(self, port, timeout=1):
		self.ser = serial.Serial(port, 9600, timeout=timeout)
		if self.ser.isOpen():
			print('[*] Порт ' + self.ser.name + ' открыт...')
	def send(self, cmd):
		cmd = cmd+'\r\n'
		self.ser.write(cmd.encode('ascii'))
	def receive(self, nBytes=32):
		ans = self.ser.read(nBytes)
		return ans.decode()
	# -------- команды GPD73303
	def getIDN(self):
		self.send('*IDN?')
		return self.receive()
	def setI(self, channel, current):
		# Настроить максимальный ток
		cmd = 'ISET%d:%.3f'%(channel, current)
		self.send(cmd)
	def getIMax(self, channel):
		# считать настройку макс. тока
		cmd = 'ISET%d?'%(channel,)
		self.send(cmd)
		ans = self.receive()
		i = float(ans.split('A')[0])
		return i
	def getI(self, channel):
		# фактический ток
		cmd = 'IOUT%d?'%(channel,)
		self.send(cmd)
		ans = self.receive()
		i = float(ans.split('A')[0])
		return i
	def setU(self, channel, voltage):
		# Настроить максимальное напряжение
		cmd = 'VSET%d:%.3f'%(channel, voltage)
		self.send(cmd)
	def getUMax(self, channel):
		# считать настройку макс. напряжения
		cmd = 'VSET%d?'%(channel,)
		self.send(cmd)
		ans = self.receive()
		v = float(ans.split('V')[0])
		return v
	def getU(self, channel):
		# фактическое напряжение
		cmd = 'VOUT%d?'%(channel,)
		self.send(cmd)
		ans = self.receive()
		v = float(ans.split('V')[0])
		return v
	# константы
	INDEPENDENT = 0
	SERIES = 1
	PARALLEL = 2
	def setMode(self, mode=INDEPENDENT):
		# режим
		self.send('TRACK%d'%(mode,))
	def setOut(self, enable=False):
		# подключение/отключение входов
		if enable:
			self.send('OUT1')
		else:
			self.send('OUT0')
	def getStatus(self):
		self.send('STATUS?')
		bytestring = self.ser.read(1)
		return bytestring
		#byte = bytestring[0]
		#Bits = np.unpack(byte)



if __name__ == "__main__":
	# парсим командную строку
	import sys
	import argparse
	parser = argparse.ArgumentParser(add_help=True)
	parser.add_argument("--port", type=str,
					 help="имя порта с подключенным источником GPD73303. В Linux обычно /dev/ttyUSB0, в Win - COM7")
	parser.add_argument("--dataFile", type=str, nargs='?', const='result.txt', default='result.txt',
					 help="Имя выходного файла с измерениями ВАХ, столбцы U, I")
	parser.add_argument('--Umin', type=float, nargs='?', const=0.5, default=0.5,
					 help="Минимальное напряжение, с которого начнется измерение ВАХ")
	parser.add_argument('--Umax', type=float, nargs='?', const=0, default=0,
					 help="Максимальное напряжение, им закончится измерение ВАХ")
	parser.add_argument('--Imax', type=float, nargs='?', const=0.1, default=0.1,
					 help="Максимальный ток на измерениях. Ограничьте его правильно! По умолчанию 0,1А.")
	parser.add_argument("-c", '--channel', nargs='?', const=1, type=int, default=1,#action='store_const', const=12, #
					 help="номер канала на источнике (1/2)")

	#parser.add_argument("-v", "--verbose", action="store_true",
	#				 help="печатать промежуточные результаты при аппроксимации")
	#parser.add_argument("-g", "--graph", action="store_true",
	#				 help="рисовать результаты на графиках")
	parser.add_argument("-k", type=int, nargs='?', const=20, default=20, #action='store_const', const=12, #
					 help="количество точек графика, по умолчанию 20")

	#print('+++', sys.argv[1:])
	args = parser.parse_args(sys.argv[1:])


	if not(args.port is None):
		print(args)
		# python3 livc.py --port "/dev/ttyUSB0" --Umin 0.8 --Umax 1.0 --Imax 0.3
		gpd = GPD73303(port=args.port)

		ch = args.channel
		gpd.setI(ch, args.Imax)
		gpd.setU(ch, args.Umin)
		gpd.setOut(True)
		v = gpd.getU(ch)
		i = gpd.getI(ch)

		V = np.linspace(args.Umin, args.Umax, args.k)
		vF = []
		iF = []
		for v in V:
			gpd.setU(ch, v)
			time.sleep(0.1)
			vF.append(gpd.getU(ch))
			iF.append(gpd.getI(ch))

		gpd.setOut(False)

		f = plt.figure(0)
		plt.clf()
		plt.plot(vF[1:], iF[1:],'-*')
		plt.xlabel('U, B')
		plt.ylabel('I, A')
		plt.grid()
		f.show()

		np.savetxt(args.dataFile, np.transpose([vF,iF]))

		input('Нажимите любую клавишу для продолжения...')
	print('Готово!')