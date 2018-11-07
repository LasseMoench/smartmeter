import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import sys, os
import sqlite3

from GUI.plot_widgets import MainPlot
from GUI.tool_widgets import MainToolBox
from GUI.helper_classes import Task


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


