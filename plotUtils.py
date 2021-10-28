import numpy as np
import pyqtgraph as pg
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

class plotUtils():
    def __init__(self, time_length=100, layout=None):
        self.data = {}
        self.time_length=time_length
        if layout is None:
            self.win = pg.GraphicsLayoutWidget(show=True, title="plot")
        else:
            self.win = pg.GraphicsLayoutWidget()
            layout.addWidget(self.win)
        self.plot = self.win.addPlot()
        self.plot.addLegend()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def update(self):
        for key in self.data.keys():
            self.data[key]['curve'].setData(self.data[key]['data'])

    def add_line(self, name, color, linetype=QtCore.Qt.SolidLine):
        if name not in self.data.keys():
            self.data[name] = {}
            self.data[name]['data'] = np.zeros(shape=(self.time_length,))

        self.data[name]['color'] = color
        self.data[name]['linetype'] = linetype
        self.data[name]['curve'] = self.plot.plot(name=name)
        self.data[name]['curve'].setPen(color=color, style=linetype)

    def add_data(self, name, data):
        if name not in self.data.keys():
            return
        self.data[name]['data'] = np.concatenate((self.data[name]['data'], data))
        if self.data[name]['data'].shape[0] > self.time_length:
            self.data[name]['data'] = self.data[name]['data'][-self.time_length:]

plotu = None

def update():
    global plotu
    data = np.random.normal(size=(100,))
    plotu.add_data('test1', data)

        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    plotu = plotUtils()
    plotu.add_line('test1', (255,0,0))
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(70)
    # window.showFullScreen()
    sys.exit(app.exec_())

        


