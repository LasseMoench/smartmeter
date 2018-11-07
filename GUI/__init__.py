"""
This module contains all the modules and subpackages required to run the smartmeter-gui.
"""

from GUI.version import version as smartmeter_version

title = "SmartMeter Graphical User Interface"

description_short = 'Python based tool for displaying power consumption data from a remote sqlite database'

version = smartmeter_version

author = "Lasse Moench and Shashwat Sridhar"

about = """
        {0}

        {1}

        Features
        ========

        * Completely written in Python 3 and PyQt5.
        * Shows an overview of power consumption from from data stored on a remote sqlite database.
        * Displays a histogram of the consumed power in time bins of chosen width.
        * Provides a flexible and modular graphical user interface.
        * Utilizes efficient plotting libraries (pyqtgraph).

        Version: {2}

        """.format(title, description_short, version, author)
