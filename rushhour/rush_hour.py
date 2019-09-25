import sys, time, threading, random, re

from PyQt5 import QtCore, uic, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

Ui_welcome_screen, QtBaseClass = uic.loadUiType("welcome_dialog.ui" )
game_screen, QtBaseClass = uic.loadUiType("game_dialog.ui")
LEVEL_BTN_W = 5
LEVEL_BTN_H = 8
LEVEL = 'Level '
FIELD_SIZE = 600
UNIT_SIZE = FIELD_SIZE / 6
X_OFFSET = 100
Y_OFFSET = 10
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
ARROW_UP = 1
ARROW_DOWN = 2
ARROW_LEFT = 3
ARROW_RIGHT = 4

class MainGame(QtWidgets.QDialog,game_screen):
	def __init__(self, levelNo):
		QtWidgets.QDialog.__init__(self)	
		game_screen.__init__(self)
		self.setupUi(self)
		self.levelNo = levelNo
		self.setWindowTitle("Level " + levelNo)
		self.setStyleSheet(None)
		self.data = self.parseData()
		# print(self.data)
		self.drawGame()

	def drawGame(self):
		#Draw cars
		for i in range(len(self.data)):
			self.data[i].draw()
		
	def paintEvent(self, e):
		#Draw boarders
		qp = QPainter()
		qp.begin(self)
		pen_board = QPen(QColor(255, 255, 0, 127))
		pen_board.setWidth(10)
		qp.setPen(pen_board)
		qp.drawRect(X_OFFSET - 5,Y_OFFSET - 5,FIELD_SIZE + 10,FIELD_SIZE + 10)
		pen_door = QPen(QColor(0, 255, 0, 127))
		pen_door.setWidth(10)
		qp.setPen(pen_door)
		qp.drawLine(X_OFFSET + FIELD_SIZE + 5, Y_OFFSET + UNIT_SIZE * 2, X_OFFSET + FIELD_SIZE + 5, Y_OFFSET + UNIT_SIZE * 3)
		qp.end()

	def on_quit_released(self):
		self.close()
		gameWindow.show()

	def parseData(self):
		with open('game.data','r') as f:
			for _ in range(int(self.levelNo)):
				dataline = f.readline()

		rawData = list(filter(None, re.split(r'\||\&',dataline.rstrip())))
		cars = []
		for i in range(int(len(rawData) / 6)):
			aCar = Car(int(rawData[i*6]), int(rawData[i*6 + 1]), int(rawData[i*6 + 2]) \
				, True if rawData[i*6 + 3] == 'true' else False, \
				True if rawData[i*6 + 4] == 'true' else False, None, self)
			cars.append(aCar)
		return cars

class Arrow(QLabel):
	def __init__(self, x, y, direction,parentWidget):
		super(Arrow, self).__init__(parentWidget)
		self.direction = direction
		self.x = x
		self.y = y
		self.parent = parentWidget
		self.move(UNIT_SIZE * self.x + X_OFFSET + 15,UNIT_SIZE * self.y + Y_OFFSET + 15)
		src = "img/arrow" + str(self.direction) + ".png"
		pixmap = QPixmap(src)
		pixmap = pixmap.scaledToWidth(UNIT_SIZE * 0.75)
		self.setPixmap(pixmap)
		self.show()

	def __str__(self):
		return str(self.x) + " : " + str(self.y)

class Car(QLabel):
	def __init__(self, x, y, length, vertical, main, name, parentWidget):
		super(Car, self).__init__(parentWidget)
		self.x = x
		self.y = y
		self.length = length
		self.vertical = vertical
		self.main = main
		self.name = name
		self.setCarImage()
		self.parent = parentWidget
		self.hide()
		self.direction = 1 # means always x+1 or y+1 , goes to right bottom coner by default. 0 means cannot move.
		self.arrow = None
		
	def setCarImage(self):
		src = ""
		if self.main:
			src = "img/car_main.png"
		elif self.length == 2: #car
			src = "img/car" + str(random.randint(1,4))+ ("_vertical" if self.vertical else "") + ".png"
		elif self.length == 3: #truck
			src = "img/truck" + str(random.randint(1,2))+ ("_vertical" if self.vertical else "") + ".png"
		# print(src)
		pixmap = QPixmap(src)#.scaled(100, 200)
		if self.vertical:
			pixmap = pixmap.scaledToWidth(UNIT_SIZE)
		else:
			pixmap = pixmap.scaledToHeight(UNIT_SIZE)
		self.setPixmap(pixmap)

	def draw(self):
		self.show()
		self.move(UNIT_SIZE * self.x + X_OFFSET,UNIT_SIZE * self.y + Y_OFFSET)

	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton: self.moveCar()

	def enterEvent(self, event):
		self.showArrow()

	def showArrow(self):
		if self.arrow is not None: self.arrow.hide()
		self.decideMoveDirection()
		if self.direction != 0:
			if self.vertical:
				if self.direction == 1:
					self.arrow = Arrow(self.x, self.y + self.length, ARROW_DOWN, self.parent)
				elif self.direction == -1:
					self.arrow = Arrow(self.x, self.y - 1, ARROW_UP, self.parent)
			else:
				if self.direction == 1:
					self.arrow = Arrow(self.x + self.length, self.y, ARROW_RIGHT, self.parent)
				elif self.direction == -1:	
					self.arrow = Arrow(self.x - 1, self.y, ARROW_LEFT, self.parent)


	def leaveEvent(self, event):
		if self.arrow is not None: self.arrow.hide()

	def moveCar(self):
		# print('move ' + self.direction)
		if self.direction == 0: return
		if self.vertical and self.direction == 1:
			self.y += 1
		elif self.vertical and self.direction == -1:
			self.y -= 1
		elif not self.vertical and self.direction == 1:
			self.x += 1
		elif not self.vertical and self.direction == -1:
			self.x -= 1
		self.draw()
		self.showArrow()
				
	def decideMoveDirection(self):
		points = []
		for i in self.parent.data:
			points.append(QPoint(i.x, i.y))
			if i.length == 2:
				if i.vertical:
					points.append(QPoint(i.x, i.y + 1))
				else:
					points.append(QPoint(i.x + 1, i.y))
			else:
				if i.vertical:
					points.append(QPoint(i.x, i.y + 1))
					points.append(QPoint(i.x, i.y + 2))
				else:
					points.append(QPoint(i.x + 1, i.y))
					points.append(QPoint(i.x + 2, i.y))
			
		if self.vertical:
			if self.direction == 1 or self.direction == 0:
				if QPoint(self.x, self.y + self.length) in points or self.y + self.length >= 6:
					self.direction = 0
				else:
					self.direction = 1
					return
				if self.y - 1 < 0 or QPoint(self.x, self.y - 1) in points:
					self.direction = 0
				else: 
					self.direction = -1
					return
			elif self.direction == -1:
				if self.y - 1 < 0 or QPoint(self.x, self.y - 1) in points:
					self.direction = 0
				else: 
					self.direction = -1
					return
				if QPoint(self.x, self.y + self.length) in points or self.y + self.length >= 6:
					self.direction = 0
				else:
					self.direction = 1
					return
		else:
			if self.direction == 1 or self.direction == 0:
				if QPoint(self.x  + self.length, self.y) in points or self.x + self.length >= 6:
					self.direction = 0
				else:
					self.direction = 1
					return
				if self.x - 1 < 0 or QPoint(self.x - 1, self.y ) in points:
					self.direction = 0
				else: 
					self.direction = -1
					return
			elif self.direction == -1:
				if self.x - 1 < 0 or QPoint(self.x - 1, self.y ) in points:
					self.direction = 0
				else: 
					self.direction = -1
					return
				if QPoint(self.x  + self.length, self.y) in points or self.x + self.length >= 6:
					self.direction = 0
				else:
					self.direction = 1
					return

class GameWelcomeWindow(QtWidgets.QMainWindow, Ui_welcome_screen):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)	
		Ui_welcome_screen.__init__(self)
		self.setupUi(self)
		self.setWindowTitle("Rush Hour")
		self.setStyleSheet("background-image: url(img/concrete.jpeg);")
		levelGrid = self.findChild(QGridLayout, "levelGrid")
		levelBtns = [[0 for x in range(LEVEL_BTN_W)] for y in range(LEVEL_BTN_H)] 
		for i in range(LEVEL_BTN_W):
			for j in range(LEVEL_BTN_H):
				btn = QPushButton(LEVEL + str(i * 8 + j + 1))
				levelGrid.addWidget(btn,i,j)
				levelBtns[j][i] = btn
		for i in range(LEVEL_BTN_W):
			for j in range(LEVEL_BTN_H):
				levelBtns[j][i].clicked.connect(self.clickBtn)

	def clickBtn(self):
		level = self.sender().text()[len(LEVEL):]
		# print(level)
		game = MainGame(level)
		game.show()
		self.close()
		game.exec_()

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	gameWindow = GameWelcomeWindow()
	gameWindow.show()
	sys.exit(app.exec_())

