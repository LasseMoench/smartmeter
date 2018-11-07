import datetime
import tzlocal
import os

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

TS_MULT_us = 1e5
local_time_zone = tzlocal.get_localzone()


def int2dt(ts):
    return datetime.datetime.fromtimestamp(float(ts), local_time_zone)


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [int2dt(value).strftime("%H:%M:%S") for value in values]


class Task(QtCore.QThread):

    def __init__(self, local_db_location):
        QtCore.QThread.__init__(self)
        self.command = "scp -q pi@bergerhoehle.de:/home/pi/smartmeter/API/energy.db " + local_db_location

    def run(self):
        os.system(self.command)