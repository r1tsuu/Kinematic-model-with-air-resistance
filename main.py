
# Kinematic Model.
#
# The program solving a system of differntial equations from a initial options which helps SciPy and shows a body
# trajectory which helps MatPlotLib.
# 
# Current version: 0.1. Created by 7eventeen.
#



from PyQt5 import QtCore, QtGui, QtWidgets
from pythongui4 import Ui_MainWindow
from scipy import integrate
from random import randint
from math import sin, cos, pi, floor
import numpy as np
import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys


# GLOBAL CONSTANTS:

g = 9.80665 # (Gravity acceleration on the Earth), m/s^2

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=7, height=4, dpi=100):
        """ Init the main MatPlotLib figure. """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor('#63FF63')
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.axes.set_facecolor('#63FF63')

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class Graph(MplCanvas):
    """ The graph, which shows at the start program. """
    def compute(self):
        x = []
        y = []
        self.axes.set_xlim(0, 6)
        self.axes.set_ylim(0, 4)
        self.axes.plot(x, y)


class GraphTrajectoryAnimation(animation.FuncAnimation, MplCanvas):
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)

    def compute(self, x, y, m, xlim, ylim):
        self.axes.set_xlim(0, xlim)
        self.axes.set_ylim(0, ylim)
        self.graphfunction, = self.axes.plot([], [], lw=2)
        self.dot, = self.axes.plot([], [], 'o', color='red')
        self.initgraph(x, y, m)


    def animation(self, i, x, y, m):
        if i * m >= len(x) or i * m >= len(y):
            self.graphfunction.set_data(x[:i*m], y[:i*m])
        else:
            self.graphfunction.set_data(x[:i*m], y[:i*m])
            self.dot.set_data(x[i*m], y[i*m])

    def initgraph(self, x, y, m, interval=50):
         x, y, m = x, y, m
         self.graph_id = animation.FuncAnimation(self.fig, self.animation, fargs=(x, y, m),
                                                 repeat=False, interval=interval, frames=400)


class SolveSystemOfADifferentialEquations:
    def __init__(self, ws, m, k, angle, v0, tlimit=20):
        self.k = k  # k is a drag cofficient, https://dynref.engr.illinois.edu/afp.html
        self.angle = angle
        self.m = m
        self.ws = ws
        self.v0 = v0
        self.v0_x = self.v0 * cos(self.angle)
        self.v0_y = self.v0 * sin(self.angle)
        self.kdivm = self.k / self.m
        self.time = np.arange(0, tlimit, 0.0005)

    def xmodel(self, X, t):
        x = X[0]
        dx = X[1]
        zdot = [ [], [] ]
        zdot[0] = dx
        zdot[1] = -self.kdivm * dx + self.ws    # init differential equation >>> dvx/dt = -k/m * vx + ws (1)
        return zdot

    def ymodel(self, Y, t):
        y = Y[0]
        dy = Y[1]
        zdot = [ [], [] ]
        zdot[0] = dy
        zdot[1] = -g - self.kdivm * dy          # init differntial equation >>> dvy/dt = -g - k/m * vy (2)
        return zdot

    def solveX(self):
        x = integrate.odeint(self.xmodel, [0, self.v0_x], self.time)  # solve (1)
        return x

    def solveY(self):
        y = integrate.odeint(self.ymodel, [0, self.v0_y], self.time)  # solve (2)
        return y


class ApplicationWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        self.layout = QtWidgets.QVBoxLayout(self.main_widget)    # add main layout to use MPL graphics
        standartgraph = Graph()
        self.layout.addWidget(standartgraph)

        self.initbuttons()

    def start(self):
        try:    # mass cannot be zero, so if you input that, you get a error. Use try to fix it.
            ws = float(self.textEdit_1.toPlainText())
            m = float(self.textEdit_2.toPlainText())
            k = float(self.textEdit_3.toPlainText())
            angle = float(self.textEdit_4.toPlainText()) * (pi / 180)
            v0 = float(self.textEdit_5.toPlainText())
            xlim = float(self.textEdit_7.toPlainText())
            ylim = float(self.textEdit_8.toPlainText())
            mi = floor(float((self.textEdit_9.toPlainText())))

            calculusvalues = SolveSystemOfADifferentialEquations(ws, m, k, angle, v0)
            X = calculusvalues.solveX()
            Y = calculusvalues.solveY()
            x = []
            y = []

            for j in range(1, len(Y)):
                if Y[j][0] > 0:
                    x.append(X[j][0])
                    y.append(Y[j][0])
                else:
                    break
            i = len(y) - 1

            trajectory = GraphTrajectoryAnimation()
            trajectory.compute(x, y, mi, xlim, ylim)

            self.layout.removeWidget(self.layout.itemAt(0).widget())
            self.layout.addWidget(trajectory)
            flyingtime = calculusvalues.time[i]
            self.textEdit_6.setPlainText('%.3f' % flyingtime)

        except ZeroDivisionError as e:
            print('error, mass of the body cannot be zero!', e)
        else:
            return

    def exit(self):
        sys.exit(1)

    def initbuttons(self):
        self.pushButton_3.clicked.connect(self.start)
        self.pushButton_1.clicked.connect(self.exit)


def main():
    global app
    app = QtWidgets.QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()