import sys
from PyQt5.QtWidgets import *
import PyQt5
import ctypes
import colour
import json
import paho.mqtt.client as mqtt
import threading


class Window(QWidget):
	currentTopic = ""
	state = "off"

	def __init__(self, topics):
		myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
		super().__init__()
		# css = open("style.css","r+")
		# self.styleSheet = css.read()
		# css.close()
		self.color = [255, 255, 255]
		self.manual = True
		self.init_ui(topics)
		# thread1 = threading.Thread(target = self.connect())
		# thread1.start()
		self.connect()

	def init_ui(self, topics):
		# set window properties
		self.resize(300, 400)
		self.center()
		self.setWindowTitle("Smart Light Control")
		self.setWindowIcon(PyQt5.QtGui.QIcon("icon.ico"))

		# create layout
		self.layout = QGridLayout()
		self.setLayout(self.layout)  # assignt the layout to th window

		# create elements:
		# create label
		self.label1 = PyQt5.QtWidgets.QLabel("Select devices:")
		self.label1.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
		self.layout.addWidget(self.label1, 0, 0)
		# create combobox
		self.comboBox = PyQt5.QtWidgets.QComboBox()

		# self.updateTopics(topics)

		Window.currentTopic = self.comboBox.currentText()
		self.comboBox.currentTextChanged.connect(self.onComboboxChanged)
		self.layout.addWidget(self.comboBox, 0, 1, 1, 2)
		# create manual/automatic radio buttons
		self.groupbox = QGroupBox("")
		self.hbox = QGridLayout()
		self.groupbox.setLayout(self.hbox)
		self.groupbox.setFixedHeight(50)
		self.layout.addWidget(self.groupbox, 1, 0, 1, 3)
		self.radiobutton1 = QRadioButton("Automatic")
		self.hbox.addWidget(self.radiobutton1, 0, 0)
		self.radiobutton2 = QRadioButton("Manual")
		self.hbox.addWidget(self.radiobutton2, 0, 1)
		self.radiobutton3 = QRadioButton("Off")
		self.hbox.addWidget(self.radiobutton3, 0, 2)
		self.radiobutton2.setChecked(True)
		self.radiobutton1.toggled.connect(self.radio1Clicked)
		self.radiobutton2.toggled.connect(self.radio2Clicked)
		self.radiobutton3.toggled.connect(self.radio3Clicked)
		self.radiobutton1.setStyleSheet("margin-left:10%; margin-right:10%;")
		self.radiobutton2.setStyleSheet("margin-left:10%; margin-right:10%;")
		self.radiobutton3.setStyleSheet("margin-left:10%; margin-right:10%;")
		# create second groupbox
		self.groupbox2 = QGroupBox("")
		self.gridLayout2 = QGridLayout()
		self.groupbox2.setLayout(self.gridLayout2)
		self.layout.addWidget(self.groupbox2, 2, 0, 1, 3)
		# create intensity row
		self.label2 = PyQt5.QtWidgets.QLabel("Brightness")
		self.label2.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
		self.gridLayout2.addWidget(self.label2, 4, 0)
		self.intensitySlider = QSlider(PyQt5.QtCore.Qt.Horizontal)
		self.intensitySlider.setFocusPolicy(PyQt5.QtCore.Qt.StrongFocus)
		self.intensitySlider.setSingleStep(1)
		self.intensitySlider.valueChanged.connect(self.intensityChange)
		self.gridLayout2.addWidget(self.intensitySlider, 4, 1, 1, 2)
		# create light temperature row
		self.label3 = PyQt5.QtWidgets.QLabel("Light temperature")
		self.label3.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
		self.gridLayout2.addWidget(self.label3, 5, 0)
		self.temperatureSlider = QSlider(PyQt5.QtCore.Qt.Horizontal)
		self.temperatureSlider.setFocusPolicy(PyQt5.QtCore.Qt.StrongFocus)
		self.temperatureSlider.setSingleStep(1)
		self.temperatureSlider.valueChanged.connect(self.temperatureChange)
		self.gridLayout2.addWidget(self.temperatureSlider, 5, 1, 1, 2)
		# create light RGB row
		self.label4 = PyQt5.QtWidgets.QLabel("RGB")
		self.label4.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
		self.gridLayout2.addWidget(self.label4, 6, 0)
		self.rgbButton = PyQt5.QtWidgets.QPushButton("Select RGB value")
		self.rgbButton.clicked.connect(self.pickColor)
		self.gridLayout2.addWidget(self.rgbButton, 6, 1, 1, 2)
		# create the selected value label
		self.label5 = PyQt5.QtWidgets.QLabel()
		self.label5.setAutoFillBackground(True)  # This is important!!
		self.updateColorLabel()
		self.label5.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
		self.gridLayout2.addWidget(self.label5, 7, 0, 1, 1)
		# create the apply button
		self.applyButton = QPushButton('Apply')
		self.applyButton.setMinimumSize(100, 50)
		self.applyButton.resize(100, 100)
		self.gridLayout2.addWidget(self.applyButton, 7, 1, 1, 2)
		self.applyButton.clicked.connect(self.applyClicked)

		self.radio1Clicked()
		self.radio2Clicked()
		self.radio3Clicked()

		self.show()

	def updateTopics(self, topics):
		print('adding topics ' + str(topics))
		self.comboBox.clear()
		self.comboBox.addItems(topics)

	def applyClicked(self):
		self.send_light_update()

	def send_light_update(self):
		color = {'r': self.color[0], 'g': self.color[1], 'b': self.color[2]}
		data = {'type': 'light', 'state': self.state, 'color': color, 'intensity': 255, 'temperature': 255}
		msg = {'topic': self.currentTopic, 'data': data}

		self.client.publish('interface', json.dumps(msg))
		print('published ' + str(msg))

	def radio1Clicked(self):
		if self.radiobutton1.isChecked():
			print("Set to Automatic")
			self.state = 'auto'
			self.manual = False
			self.intensitySlider.setEnabled(False)
			self.temperatureSlider.setEnabled(False)
			self.rgbButton.setEnabled(False)
			self.label2.setEnabled(False)
			self.label3.setEnabled(False)
			self.label4.setEnabled(False)
			self.label5.setEnabled(False)
			self.applyButton.setEnabled(False)
			self.client.publish(Window.currentTopic, "auto")

			self.send_light_update()

	def radio2Clicked(self):
		if self.radiobutton2.isChecked():
			print("Set to Manual")
			self.state = 'on'
			self.manual = True
			self.intensitySlider.setEnabled(True)
			self.temperatureSlider.setEnabled(True)
			self.rgbButton.setEnabled(True)
			self.label2.setEnabled(True)
			self.label3.setEnabled(True)
			self.label4.setEnabled(True)
			self.label5.setEnabled(True)
			self.applyButton.setEnabled(True)

	def radio3Clicked(self):
		if self.radiobutton3.isChecked():
			print("Set to OFF")
			self.state = 'off'
			self.manual = False
			self.intensitySlider.setEnabled(False)
			self.temperatureSlider.setEnabled(False)
			self.rgbButton.setEnabled(False)
			self.label2.setEnabled(False)
			self.label3.setEnabled(False)
			self.label4.setEnabled(False)
			self.label5.setEnabled(False)
			self.applyButton.setEnabled(False)
			self.client.publish(Window.currentTopic, "off")

			self.send_light_update()

	def intensityChange(self):
		value = self.intensitySlider.value()
		new = int(((value + 1) * 2.56) - 1)
		# print(new, new, new)
		self.color = [new, new, new]
		self.updateColorLabel()

	def temperatureChange(self):
		value = self.temperatureSlider.value() + 1
		# range is 1100K to 11 000K
		K = int(1000 + (value * 120))
		print("Kelvins: ", K)
		xy = colour.CCT_to_xy(K)
		# print("xy", xy)
		xyz = colour.xy_to_XYZ(xy)
		# print("xyz", xyz)
		rgb = colour.XYZ_to_sRGB(xyz)
		r = int(min(1, max(0, rgb[0])) * 255)
		g = int(min(1, max(0, rgb[1])) * 255)
		b = int(min(1, max(0, rgb[2])) * 255)
		self.color = [r, g, b]
		# print("rgb", self.color)
		self.updateColorLabel()

	def pickColor(self):
		color = PyQt5.QtWidgets.QColorDialog.getColor()
		self.color = [color.red(), color.green(), color.blue()]
		self.updateColorLabel()

	def updateColorLabel(self):
		self.label5.setText("R: " + str(self.color[0]) + "\nG: " + str(self.color[1]) + "\nB: " + str(self.color[2]))
		color = PyQt5.QtGui.QColor(self.color[0], self.color[1], self.color[2])
		alpha = 255
		values = "{r}, {g}, {b}, {a}".format(r=color.red(),
											 g=color.green(),
											 b=color.blue(),
											 a=alpha
											 )
		self.label5.setStyleSheet("QLabel { background-color: rgba(" + values + "); }")

	def onComboboxChanged(self):
		Window.currentTopic = self.comboBox.currentText()

	# self.connect()

	def center(self):
		# geometry of the main window
		qr = self.frameGeometry()
		# center point of screen
		centerPoint = QDesktopWidget().availableGeometry().center()
		# move rectangle's center point to screen's center point
		qr.moveCenter(centerPoint)
		# top left of rectangle becomes top left of window centering it
		self.move(qr.topLeft())

	def connect(self):
		self.client = mqtt.Client()
		self.client.connect("165.22.79.210", port=65020)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message

		self.client.loop_start()

	def on_connect(self, client, userdata, flags, rc):
		print("Connected with result code " + str(rc))
		# print("Subscribing to", Window.currentTopic, "\n")
		# client.subscribe(Window.currentTopic)
		client.subscribe('status')
		client.publish('status-request', '{"location":"all"}')

	def on_message(self, client, userdata, msg):
		global currentTopic, topics
		if msg.topic == 'status':
			payload = msg.payload.decode('UTF-8')
			message = json.loads(payload)
			if message['type'] == 'all':
				topics = message['identifiers']
				print(topics)
				currentTopic = topics[0]
				self.updateTopics(topics)
				print('should be adding topics...')


def parse_topics():  # Not used
	global topics
	topics = []
	with open("topics.txt", "r+") as f:
		topics = f.readlines()
	for idx, topic in enumerate(topics):
		topics[idx] = topic.rstrip("\n")
		topics[idx] = topics[idx].rstrip("\r\n")
	f.close()
	return topics


if __name__ == "__main__":
	topics = []  # parse_topics()
	app = QApplication(sys.argv)
	window = Window(topics)
	# app.setStyleSheet(window.styleSheet)
	sys.exit(app.exec_())
