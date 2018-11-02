import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import sys
from os import path
import sqlite3
import datetime, tzlocal

TS_MULT_us = 1e5
local_time_zone = tzlocal.get_localzone()

def int2dt(ts):
    return datetime.datetime.fromtimestamp(float(ts), local_time_zone)


class Main(QtGui.QMainWindow):

    def __init__(self, database_path=None, *args, **kwargs):
        QtGui.QMainWindow.__init__(self, *args, **kwargs)

        self.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks |
                            QtGui.QMainWindow.AllowNestedDocks |
                            QtGui.QMainWindow.GroupedDragging)

        self.main_plot_dock = QtGui.QDockWidget("Central Dock")
        self.main_plot_widget = MainPlot()
        self.main_plot_dock.setWidget(self.main_plot_widget)

        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.main_plot_dock, QtCore.Qt.Vertical)

        if database_path is not None:
            self.database_path = database_path
        else:
            self.database_path = "/home/sridhar/PycharmProjects/smartmeter/API/energy.db"

        if not path.exists(self.database_path):
            print("Invalid/non-existent database file requested, quitting!", file=sys.stderr)
            sys.exit(0)

        self.read_interval = 2000  # milliseconds
        self.limit = 1000
        self.bin_step = 100

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self.read_interval)

    @staticmethod
    def create_connection(database_path):
        """
        Create database connection to the SQLite database at the given path.

        If the database cannot be read, return None.

        :param database_path:
        :return: connection object, or None
        """
        try:
            conn = sqlite3.connect(database_path)
            return conn
        except Exception as e:
            print("Error in database path: {0}".format(database_path), file=sys.stderr)
            print(e)

        return None

    def get_timestamps(self, conn):
        """
        Fetch all timestamps from the loaded database file.

        :return: numpy array of shape (M,) where M is the number of timestamps
        """
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp from energy")
        return np.array(cursor.fetchall())[:, 0]

    def convert_to_time(self, timestamp_array):
        return np.array([int2dt(ts) for ts in timestamp_array])

    def update_plot(self):
        with self.create_connection(self.database_path) as conn:
            times = self.get_timestamps(conn)
            hist, bins = np.histogram(times, bins=np.arange(times[0], times[-1], self.bin_step))
            self.main_plot_widget.update_curve(x=bins[:-1], y=hist)


class MainPlot(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.layout = QtGui.QGridLayout()

        self.plot_widget = pg.PlotWidget(background='k', axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.layout.addWidget(self.plot_widget, 0, 0)

        self.plot_item = self.plot_widget.plotItem
        self.curve = self.plot_item.plot()

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

    def decorate_plot(self):
        self.show_grid()
        self.set_x_label("Time")
        self.set_y_label("Power")
        self.set_plot_title("Power Consumption at the Bergerhoehle")

    def update_curve(self, x, y):
        self.curve.setData(x=x, y=y)


class DarkPalette(QtGui.QPalette):
    """Class that inherits from pyqtgraph.QtGui.QPalette and renders dark colours for the application."""

    def __init__(self):
        QtGui.QPalette.__init__(self)
        self.setup()

    def setup(self):
        self.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 50, 47))
        self.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
        self.setColor(QtGui.QPalette.Base, QtGui.QColor(30, 27, 24))
        self.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 50, 47))
        self.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 255))
        self.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
        self.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
        self.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 50, 47))
        self.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
        self.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
        self.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        self.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        self.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(0, 0, 0))


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [int2dt(value).strftime("%H:%M:%S.%f") for value in values]


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(DarkPalette())

    pg.setConfigOption('background', 'k')
    pg.setConfigOption('foreground', 'w')
    pg.setConfigOption('useOpenGL', True)

    m = Main()
    m.show()
    sys.exit(app.exec())
