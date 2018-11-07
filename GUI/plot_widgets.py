from pyqtgraph.Qt import QtGui, QtWidgets
from pyqtgraph import PlotWidget
import numpy as np

from GUI.helper_classes import TimeAxisItem


class MainPlot(QtWidgets.QWidget):

    def __init__(self, parent=None, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, parent=parent, *args, **kwargs)

        self.layout = QtGui.QGridLayout()

        self.plot_widget = PlotWidget(background='k', axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.layout.addWidget(self.plot_widget, 0, 0)

        self.step_mode = True
        self.plot_item = self.plot_widget.plotItem
        self.curve = self.plot_item.plot(stepMode=self.step_mode)

        self.times = None

        self.x_limit = 1000  # timestamp values
        self.bin_step = 300  # seconds
        self.power_per_tick = 13.333  # Watt-hours

        self.setLayout(self.layout)

        self.decorate_plot()

    def show_grid(self):
        self.plot_widget.plotItem.showGrid(x=True, y=True)

    def set_x_label(self, text, units=None, *args):
        self.plot_widget.plotItem.setLabel('bottom', text=text, units=units, *args)

    def set_y_label(self, text, units=None, *args):
        self.plot_widget.plotItem.setLabel('left', text=text, units=units, *args)

    def set_plot_title(self, text):
        self.plot_widget.plotItem.setTitle(title=text)

    def get_bin_step(self):
        return self.bin_step

    def get_power_per_tick(self):
        return self.power_per_tick

    def decorate_plot(self):
        self.show_grid()
        self.set_x_label("Time")
        self.set_y_label("Power", "W")
        self.set_plot_title("Power Consumption at the Bergerhoehle")

    def update_curve(self, x, y):
        self.curve.setData(x=x, y=y, stepMode=self.step_mode)

    def create_histogram(self, times):
        self.times = times
        hist, bins = np.histogram(times, bins=np.arange(times[0], times[-1], self.bin_step))
        if self.step_mode:
            self.update_curve(x=bins[:], y=hist * self.power_per_tick * (3600/self.bin_step))
        else:
            self.update_curve(x=bins[:-1], y=hist * self.power_per_tick * (3600/self.bin_step))

    def refresh_plot(self):
        times = self.times
        hist, bins = np.histogram(times, bins=np.arange(times[0], times[-1], self.bin_step))
        if self.step_mode:
            self.update_curve(x=bins[:], y=hist * self.power_per_tick * (3600/self.bin_step))
        else:
            self.update_curve(x=bins[:-1], y=hist * self.power_per_tick * (3600/self.bin_step))