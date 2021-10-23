import numpy as np
import pyqtgraph as pg

class plotUtils():

    def __init__(self, time_length=100, parent=None):
        super(plotUtils, self).__init__(parent)
        self.data = {}
        self.time_length=time_length
        self.win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
        self.plot = self.win.addPlot()

    def update(self):
        for key in self.data.keys():
            self.data[key]['curve'].setData(self.data[key]['data'])

    def add_line(self, name, color, linetype):
        if name not in self.data.keys():
            self.data[name]['data'] = np.zeros(shape=(self.time_length,))

        self.data[name]['color'] = color
        self.data[name]['linetype'] = linetype
        self.data[name]['curve'] = self.plot.plot()
        self.data[name]['curve'].setPen(color=color, style=linetype)

    def add_data(self, name, data):
        if name not in self.data.keys():
            return
        self.data[name]['data'] = np.concatenate((self.data[name]['data'], data))
        if self.data[name]['data'].shape[0] > self.time_length:
            self.data[name]['data'] = self.data[name]['data'][:-self.time_length]


        

        


