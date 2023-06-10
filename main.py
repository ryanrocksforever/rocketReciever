import sys
from datetime import time, datetime
import json
import csv
import qdarkstyle as qdarkstyle
import serial
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint
global startlogging
startlogging = False
fields = ['yaw', 'pitch', 'roll', 'xccel', 'zaccel', 'yawservo', 'pitchservo', 'altitude', 'tempurature', 'message', 'yawPID', 'pitchPID']
now = datetime.now()

filename = "./rn_flight_data_" + now.strftime("%m-%d-%Y") + ".csv"
with open(filename,'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)

class Window(QWidget):
    def __init__(self):
        super().__init__()

        # Defining a scene rect of 400x200, with it's origin at 0,0.
        # If we don't set this on creation, we can set it later with .setSceneRect
        self.scene = QGraphicsScene(0, 0, 500, 800)
        self.scenepitch = QGraphicsScene(0, 0, 500, 800)

        # Draw a rectangle item, setting the dimensions.
        self.rectyaw = QGraphicsRectItem(0, 0, 1, 500)
        self.rectyaw.setPos(250, 700)
        self.rectyaw.setRotation(180)

        brush = QBrush(Qt.GlobalColor.red)
        self.rectyaw.setBrush(brush)
        self.rectyaw2 = QGraphicsRectItem(0, 0, 5, 100)
        self.rectyaw2.setPos(247, 700)
        brush = QBrush(Qt.GlobalColor.red)
        self.rectyaw2.setBrush(brush)

        # Define the pen (line)
        pen = QPen(Qt.GlobalColor.cyan)
        pen.setWidth(10)
        self.rectyaw.setPen(pen)


        # Draw a rectangle item, setting the dimensions.
        self.rectpitch = QGraphicsRectItem(0, 0, 1, 500)
        self.rectpitch.setPos(250, 700)
        self.rectpitch.setRotation(180)

        brush = QBrush(Qt.GlobalColor.red)
        self.rectpitch.setBrush(brush)
        self.rectpitch2 = QGraphicsRectItem(0, 0, 5, 100)
        self.rectpitch2.setPos(247, 700)
        brush = QBrush(Qt.GlobalColor.red)
        self.rectpitch2.setBrush(brush)

        # Define the pen (line)
        pen = QPen(Qt.GlobalColor.darkBlue)
        pen.setWidth(10)
        self.rectpitch.setPen(pen)





        # Add the items to the scene. Items are stacked in the order they are added.

        self.scene.addItem(self.rectyaw)
        self.scene.addItem(self.rectyaw2)
        textitem = self.scene.addText("Yaw Position")
        textitem.setScale(3)
        textitem.setPos(100, 1)

        self.scenepitch.addItem(self.rectpitch)
        self.scenepitch.addItem(self.rectpitch2)
        textitem2 = self.scenepitch.addText("Pitch Position")
        textitem2.setScale(3)
        textitem2.setPos(100, 1)
        # Set all items as moveable and selectable.


        # Define our layout.
        vbox = QVBoxLayout()
        vboxinfo = QVBoxLayout()

        up = QPushButton("LAUNCH")
        up.clicked.connect(lambda:self.send_command("LAUNCH"))
        vboxinfo.addWidget(up)

        down = QPushButton("ABORT")
        down.clicked.connect(lambda:self.send_command("ABORT"))
        vboxinfo.addWidget(down)


        testPyro = QPushButton("testPyro")
        testPyro.clicked.connect(lambda:self.send_command("testPyro"))
        vboxinfo.addWidget(testPyro)

        calibrateAccel = QPushButton("calibrate MPU")
        calibrateAccel.clicked.connect(lambda:self.send_command("calibrateAccel"))
        vboxinfo.addWidget(calibrateAccel)

        calibrateTVC = QPushButton("calibrateTVC")
        calibrateTVC.clicked.connect(lambda:self.send_command("calibrateTVC"))
        vboxinfo.addWidget(calibrateTVC)

        demoLaunch = QPushButton("Demo launch")
        demoLaunch.clicked.connect(lambda:self.send_command("DEMO"))
        vboxinfo.addWidget(demoLaunch)

        startLogging = QPushButton("Start Logging")
        startLogging.clicked.connect(lambda:self.startLog())
        vboxinfo.addWidget(startLogging)

        stopLogging = QPushButton("Stop Logging")
        stopLogging.clicked.connect(lambda:self.stopLog())
        vboxinfo.addWidget(stopLogging)


        view = QGraphicsView(self.scene)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        viewpitch = QGraphicsView(self.scenepitch)
        viewpitch.setRenderHint(QPainter.RenderHint.Antialiasing)
        hbox = QHBoxLayout(self)
        hbox.addLayout(vboxinfo)
        hbox.addLayout(vbox)

        hbox.addWidget(view)
        hbox.addWidget(viewpitch)

        self.setLayout(hbox)
        self.tempWidget = QLabel("Temp: ")
        self.messageWidget = QLabel("Message: ")
        self.xaccelWidget = QLabel("Xaccel: ")
        self.yaccelWidget = QLabel("Yaccel: ")
        self.zaccelWidget = QLabel("Zaccel: ")
        self.yawpidWidget = QLabel("YawPID: ")
        self.pitchpidWidget = QLabel("PitchPID: ")
        self.speedWidget = QLabel("Vertical Speed: ")

        vboxinfo.addWidget(self.tempWidget)
        vboxinfo.addWidget(self.messageWidget)
        vboxinfo.addWidget(self.xaccelWidget)
        vboxinfo.addWidget(self.yaccelWidget)
        vboxinfo.addWidget(self.zaccelWidget)
        vboxinfo.addWidget(self.yawpidWidget)
        vboxinfo.addWidget(self.pitchpidWidget)
        vboxinfo.addWidget(self.speedWidget)

        self.graphWidgetyaw = pg.PlotWidget()
        self.graphWidgetyaw.setBackground((25,35,45))
        #pg.setPalette(pg.mkPalette("red"))
       # color = self.palette().color(QtGui.QPalette(Window()))  # Get the default window background,
        #self.graphWidgetyaw.setBackground(color)

        self.graphWidgetpitch = pg.PlotWidget()
        self.graphWidgetroll = pg.PlotWidget()
        self.graphWidgetalt = pg.PlotWidget()

        vbox.addWidget(self.graphWidgetyaw)
        vbox.addWidget(self.graphWidgetpitch)
        vbox.addWidget(self.graphWidgetroll)
        vbox.addWidget(self.graphWidgetalt)



        self.graphWidgetyaw.setTitle("Yaw graph", color="b", size="20pt")
        # Add Axis Labels
        styles = {"color": "#f00", "font-size": "20px"}
        self.graphWidgetyaw.setLabel("left", "Yaw (degrees)", **styles)
        self.graphWidgetyaw.setLabel("bottom", "Time(s)", **styles)

        self.graphWidgetpitch.setTitle("Pitch graph", color="b", size="20pt")
        # Add Axis Labels
        styles = {"color": "#f00", "font-size": "20px"}
        self.graphWidgetpitch.setLabel("left", "Pitch (degrees)", **styles)
        self.graphWidgetpitch.setLabel("bottom", "Time(s)", **styles)

        self.graphWidgetroll.setTitle("Roll graph", color="b", size="20pt")
        # Add Axis Labels
        styles = {"color": "#f00", "font-size": "20px"}
        self.graphWidgetroll.setLabel("left", "Roll (degrees)", **styles)
        self.graphWidgetroll.setLabel("bottom", "Time(s)", **styles)

        self.graphWidgetalt.setTitle("Altitude graph", color="b", size="20pt")
        # Add Axis Labels
        styles = {"color": "#f00", "font-size": "20px"}
        self.graphWidgetalt.setLabel("left", "Altitude (m)", **styles)
        self.graphWidgetalt.setLabel("bottom", "Time(s)", **styles)


        self.x = [0]  # 100 time points
        self.y = [0]

        self.xp = [0]  # 100 time points
        self.yp = [0]

        self.xr = [0]  # 100 time points
        self.yr = [0]


        self.xa = [0]  # 100 time points
        self.ya = []

        self.graphWidgetyaw.setBackground((25,35,45))
        self.data_line =  self.graphWidgetyaw.plot(self.x, self.y)


        self.graphWidgetpitch.setBackground((25,35,45))
        self.data_linep =  self.graphWidgetpitch.plot(self.xp, self.yp)

        self.graphWidgetroll.setBackground((25,35,45))
        self.data_liner =  self.graphWidgetroll.plot(self.xr, self.yr)

        self.graphWidgetalt.setBackground((25,35,45))
        self.data_linea =  self.graphWidgetalt.plot(self.xr, self.yr)


        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def up(self):
        """ Iterate all selected items in the view, moving them forward. """
        items = self.scene.selectedItems()
        for item in items:
            z = item.zValue()
            item.setZValue(z + 1)

    def down(self):
        """ Iterate all selected items in the view, moving them backward. """
        items = self.scene.selectedItems()
        for item in items:
            z = item.zValue()
            item.setZValue(z - 1)

    def rotate(self, value):
        """ Rotate the object by the received number of degrees. """
        items = self.scene.selectedItems()
        for item in items:
            item.setRotation(value)

    def send_command(self, command):
        print("sending command: " + command)
        command = " " + command + "\n"
        command = bytes(command, 'utf-8')

        ser.write(command)



    def startLog(self):
        global startlogging
        startlogging = True

    def stopLog(self):
        global startlogging
        startlogging = False


    def update_plot_data(self):
        global startlogging

        try:
            data = str(ser.readline())
            print(data)
            if "{" in str(data):
                data = data.split("}")[0] + "}"
                print(data[7:])
                data = json.loads(data[7:])
                print(data)
                #self.x = self.x[1:]  # Remove the first y element.
                #self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

                #self.y = self.y[1:]  # Remove the first
                self.y.append(data["yaw"])  # Add a new random value.

                self.x = range(0, len(self.y))

                self.data_line.setData(self.x, self.y)  # Update the data.


                #self.xp.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

                #self.y = self.y[1:]  # Remove the first
                self.yp.append(data["pitch"])  # Add a new random value.

                self.xp = range(0, len(self.yp))

                self.data_linep.setData(self.xp, self.yp)  # Update the data.

                #self.xr.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

                #self.y = self.y[1:]  # Remove the first

                self.yr.append(data["roll"])  # Add a new random value.

                self.xr = range(0, len(self.yr))

                self.data_liner.setData(self.xr, self.yr)  #

                #self.xa.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

                #self.y = self.y[1:]  # Remove the first
                self.ya.append(data["altitude"])  # Add a new random value.

                self.xa = range(0, len(self.ya))
                self.data_linea.setData(self.xa, self.ya)  # Update the data.


                self.tempWidget.setText("temp: " + str(data["tempurature"]))
                self.messageWidget.setText("message: " + str(data["message"]))
                self.xaccelWidget.setText("X accel: " + str(data["xccel"]))
                self.yaccelWidget.setText("Y accel: " + str(data["yaccel"]))
                self.zaccelWidget.setText("Z accel: " + (str(data["zaccel"])))

                try:
                    self.yawpidWidget.setText("YawPID: " + (str(data["yawPID"])))
                    self.pitchpidWidget.setText("PitchPID: " + (str(data["pitchPID"])))
                    self.speedWidget.setText("Vertical Speed: " +(str(data["speed"])))
                    self.rectyaw2.setRotation((data["yaw"]-data["yawPID"]))
                    self.rectpitch2.setRotation((data["pitch"]-data["pitchPID"]))
                except:
                    print("no yaw yet")

                self.rectyaw.setRotation(180 + data["yaw"])

                self.rectpitch.setRotation(180 + data["pitch"])


                if startlogging == True:
                    print("LOGGING")
                    csvdata = [data['yaw'], data['pitch'], data['roll'], data['xccel'], data['zaccel'], data['yawservo'], data['pitchservo'], data['altitude'], data['tempurature'], data['message'], data['yawPID'], data['pitchPID']]
                    with open(filename,'a') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerow(csvdata)

        except Exception as e:
            print("Error")
            print(e)




app = QApplication(sys.argv)

ser = serial.Serial(timeout=0.25)
ser.baudrate = 9600
ser.port = 'COM4'
ser.open()
if ser.isOpen():
    print("Serial port opened")
else:
    while not ser.isOpen():
        print("no serial open")
        time.sleep(1)


w = Window()
app.setStyleSheet(qdarkstyle.load_stylesheet())

w.show()


app.exec()


