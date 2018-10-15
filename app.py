import sys
from PyQt5 import uic, QtWidgets
import numpy as np
from time import time
import modules


qtCreatorFile = "rg.ui" # Nombre del archivo aquí.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.Draw_Button.clicked.connect(self.draw)
        self.Read_Button.clicked.connect(self.read)

    def read(self):
        direccion = (self.file_address.toPlainText())
        if direccion[-3:] == "las":
            mapa_las= modules.read_file(direccion)
            n_points = str(modules.num_datagrams(mapa_las,28,227))
            self.total_points.setText(n_points)
            self.advertising.setText("Valid file")
        elif direccion[-3:] == "ply":
            self.total_points.setText(modules.read_ply_points(direccion))
            self.advertising.setText("Valid file")
        else:
            self.advertising.setText("Enter a valid file")

    def draw(self):
        direccion = (self.file_address.toPlainText())
        if direccion[-3:] == "las":
            start_time = time()
            mapa_las= modules.read_file(direccion)
            n_points = int(self.number_points.toPlainText())
            matrix= modules.points_matrix(mapa_las, n_points)
            elapsed_time = time() - start_time
            print("Elapsed time: %.10f seconds." % elapsed_time)
            modules.dibujar(matrix,0)
            self.advertising.setText("Valid file")
        elif direccion[-3:] == "ply":
            modules.dibujar(direccion,1)
            self.advertising.setText("Valid file")
        else:
            self.advertising.setText("Enter a valid file")


if __name__ == "__main__":

    app =  QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())

"""
Data sheet
"""
