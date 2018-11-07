from pyqtgraph.Qt import QtCore, QtGui, QtWidgets


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