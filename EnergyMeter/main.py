import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import sys, os
import sqlite3
import datetime, tzlocal

TS_MULT_us = 1e5
local_time_zone = tzlocal.get_localzone()


def int2dt(ts):
    return datetime.datetime.fromtimestamp(float(ts), local_time_zone)


class Task(QtCore.QThread):

    def __init__(self, local_db_location):
        QtCore.QThread.__init__(self)
        self.command = "scp -q pi@bergerhoehle.de:/home/pi/smartmeter/API/energy.db " + local_db_location

    def run(self):
        os.system(self.command)


class Main(QtGui.QMainWindow):

    def __init__(self, local_db_path=None, *args, **kwargs):
        QtGui.QMainWindow.__init__(self, *args, **kwargs)

        if local_db_path is not None:
            self.database_path = local_db_path
        else:
            self.database_path = "/home/sridhar/PycharmProjects/smartmeter/API/energy.db"

        if not os.path.exists(self.database_path):
            print("Invalid/non-existent database file requested, quitting!", file=sys.stderr)
            sys.exit(0)

        self.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks |
                            QtGui.QMainWindow.AllowNestedDocks |
                            QtGui.QMainWindow.GroupedDragging)

        self.main_plot_dock = QtGui.QDockWidget("Central Dock")
        self.main_plot_widget = MainPlot()
        self.main_plot_dock.setWidget(self.main_plot_widget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.main_plot_dock, QtCore.Qt.Horizontal)

        self.main_tool_box_dock = QtGui.QDockWidget("Central Toolbox")
        self.main_tool_box = MainToolBox(self.main_plot_widget)
        self.main_tool_box_dock.setWidget(self.main_tool_box)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.main_tool_box_dock, QtCore.Qt.Horizontal)

        self.read_interval = 10000  # milliseconds
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.setInterval(self.read_interval)
        self.timer.start()

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
        cursor.execute("SELECT * from energy")
        return np.array(cursor.fetchall())[:, 0]

    def update_plot(self):
        try:
            fetch_data = Task(self.database_path)
            fetch_data.start()
            while fetch_data.isRunning():
                QtGui.QApplication.processEvents()
        except Exception as e:
            print(e)
            print("SSH call failed, check connection!")
            sys.exit(0)
        with self.create_connection(self.database_path) as conn:
            times = self.get_timestamps(conn)
            self.main_plot_widget.create_histogram(times)


class MainPlot(QtWidgets.QWidget):

    def __init__(self, parent=None, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, parent=parent, *args, **kwargs)

        self.layout = QtGui.QGridLayout()

        self.plot_widget = pg.PlotWidget(background='k', axisItems={'bottom': TimeAxisItem(orientation='bottom')})
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


class MainToolBox(QtWidgets.QWidget):
    """Class that houses tools to modify the plot in the MainPlot widget."""

    def __init__(self, plot_widget, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        self.plot_parent = plot_widget
        self.bin_step_upper = 1e6
        self.bin_step_lower = 60
        self.bin_step = self.plot_parent.bin_step

        self.layout_level_0 = QtGui.QGridLayout(self)
        self.histogram_options = QtGui.QGroupBox("Histogram Options")
        self.histogram_options_layout = QtGui.QGridLayout(self.histogram_options)

        w = QtGui.QWidget()
        y = QtGui.QWidget()
        l1 = QtGui.QLabel("X Range:")
        l2 = QtGui.QLabel("Bin Step (in seconds):")
        self.errorLabel = QtGui.QLabel()
        self.errorLabel.setStyleSheet("color: rgb(255, 0, 0);")

        self.ghl1 = QtGui.QHBoxLayout(w)
        self.ghl2 = QtGui.QHBoxLayout(y)

        self.binStepPlusBtn = QtGui.QPushButton("+")
        self.binStepPlusBtn.setMinimumWidth(30)
        self.binStepPlusBtn.setMaximumWidth(50)
        self.binStepEdit = QtGui.QLineEdit()
        self.binStepEdit.setMinimumWidth(30)
        self.binStepEdit.setMaximumWidth(50)
        self.binStepEdit.setText(str(plot_widget.bin_step))
        self.binStepMinusBtn = QtGui.QPushButton("-")
        self.binStepMinusBtn.setMinimumWidth(30)
        self.binStepMinusBtn.setMaximumWidth(50)

        self.rangePlusBtn = QtGui.QPushButton("+")
        self.rangePlusBtn.setMinimumWidth(30)
        self.rangePlusBtn.setMaximumWidth(50)
        self.rangeEdit = QtGui.QLineEdit()
        self.rangeEdit.setMinimumWidth(30)
        self.rangeEdit.setMaximumWidth(50)
        self.rangeEdit.setText(str(plot_widget.x_limit))
        self.rangeMinusBtn = QtGui.QPushButton("-")
        self.rangeMinusBtn.setMinimumWidth(30)
        self.rangeMinusBtn.setMaximumWidth(50)

        self.histStyleCheckbox = QtGui.QCheckBox()
        self.histStyleCheckbox.setText("Step Mode")
        self.histStyleCheckbox.setCheckState(QtCore.Qt.Checked)

        # self.ghl1.addWidget(self.rangeMinusBtn)
        # self.ghl1.addWidget(self.rangeEdit)
        # self.ghl1.addWidget(self.rangePlusBtn)

        self.ghl2.addWidget(self.binStepMinusBtn)
        self.ghl2.addWidget(self.binStepEdit)
        self.ghl2.addWidget(self.binStepPlusBtn)

        self.binStepPlusBtn.clicked.connect(self.on_step_plus)
        self.binStepMinusBtn.clicked.connect(self.on_step_minus)
        self.histStyleCheckbox.stateChanged.connect(self.step_mode_changed)
        self.binStepEdit.textChanged.connect(self.bin_step_changed)
        self.binStepEdit.returnPressed.connect(self.on_enter)

        self.histogram_options_layout.addWidget(l2, 0, 0, 1, 2)
        self.histogram_options_layout.addWidget(y, 0, 2, 1, 2)
        # self.histogram_options_layout.addWidget(l1, 1, 0, 1, 2)
        # self.histogram_options_layout.addWidget(w, 1, 2, 1, 2)
        self.histogram_options_layout.addWidget(self.histStyleCheckbox, 0, 4, 1, 2)
        self.histogram_options_layout.addWidget(self.errorLabel, 1, 4, 1, 2)

        self.histogram_options.setLayout(self.histogram_options_layout)
        self.layout_level_0.addWidget(self.histogram_options)

    def on_enter(self):
        """
        This method is called if you press ENTER on one of the line
        edit widgets.

        Redraws everything.

        """
        try:
            if self.bin_step_lower <= float(self.bin_step) <= self.bin_step_upper:
                self.plot_parent.bin_step = self.bin_step
                self.plot_parent.refresh_plot()
                self.errorLabel.setText("")
            else:
                self.errorLabel.setText("Values outside acceptable limits")
        except:
            self.errorLabel.setText("Invalid inputs!")

    def on_step_plus(self):
        """
        This method is called if you click on the plus button
        for the bin step option.

        Increments the bin step option.

        """
        bin_step = self.plot_parent.bin_step
        if (bin_step + 10) <= self.bin_step_upper:
            self.plot_parent.bin_step += 10
            self.binStepEdit.setText(str(self.plot_parent.bin_step))
            self.plot_parent.refresh_plot()

    def on_step_minus(self):
        """
        This method is called if you click on the minus button
        for the bin step option.

        Decrements the bin step option.

        """
        bin_step = self.plot_parent.bin_step
        if (bin_step - 10) >= self.bin_step_lower:
            self.plot_parent.bin_step -= 10
            self.binStepEdit.setText(str(self.plot_parent.bin_step))
            self.plot_parent.refresh_plot()

    def bin_step_changed(self, value):
        """
        This method is called if you edit the bin step option.

        Checks if the bin step is correct.

        """
        bin_step = value
        try:
            bin_step = float(bin_step)
            if self.bin_step_lower <= bin_step <= self.bin_step_upper:
                self.bin_step = bin_step
                self.errorLabel.setText("")
            else:
                self.errorLabel.setText("Value outside acceptable limits!")

        except:
            self.errorLabel.setText("Invalid input!")

    def step_mode_changed(self):

        current_step_mode = self.plot_parent.step_mode
        new_step_mode = self.histStyleCheckbox.isChecked()

        if current_step_mode != new_step_mode:
            self.plot_parent.step_mode = new_step_mode
            self.plot_parent.refresh_plot()


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
        return [int2dt(value).strftime("%H:%M:%S") for value in values]


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(DarkPalette())

    pg.setConfigOption('background', 'k')
    pg.setConfigOption('foreground', 'w')
    pg.setConfigOption('useOpenGL', True)

    if len(sys.argv) > 1:
        local_database_path = sys.argv[1]
    else:
        local_database_path = None

    m = Main(local_database_path)
    m.show()
    sys.exit(app.exec())
