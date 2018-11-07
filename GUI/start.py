import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
import sys

from GUI.main import Main
from GUI.palettes import DarkPalette


def launch():
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


if __name__ == "__main__":
    launch()
