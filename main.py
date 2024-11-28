import sys

import pyodbc
from PyQt6 import QtCore
from PyQt6.QtWidgets import *
import Add_Visit
import Residence

conn = pyodbc.connect(driver='{SQL Server}', server='127.0.0.1', database='db22207', user='User086',
                      password='{User086}};73}')
cursor = conn.cursor()

class AddVisitView(QWidget, Add_Visit.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class ListView(QMainWindow, Residence.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btnAdd.clicked.connect(self.add_visit_window)

    def add_visit_window(self):
        self.window_add_visit = AddVisitView()
        self.window_add_visit.show()

    def fill_table(self):
        query = "Select tblClient.txtClientSurname, tblClient.txtClientName, tblClient.txtClientSecondName," \
                "tblVisit.datBegin, " \
                "tblVisit.datEnt, tblVisit.intRoomNumber,tblRoom.intFlor, tblVisit.fltServiceSum From tblVisit," \
                "tblClient," \
                "tblRoom Where (tblVisit.intClientId = tblClient.intClientId) AND (tblVisit.intRoomNumber = " \
                "tblRoom.intRoomNumber) "
        cursor.execute(query)

        self.listInfo.clear()
        labels = ["Фамилия", "Имя", "Отчество", "Дата приезда", "Дата отъезда", "Номер комнаты", "Этаж",
                  "Стоимость услуг"]
        self.listInfo.setColumnCount(len(labels))
        self.listInfo.setGeometry(10, 10, 125, 100)
        self.listInfo.setHorizontalHeaderLabels(labels)

        row = cursor.fetchone()
        i = 0
        while row:
            self.listInfo.setRowCount(i + 1)
            for j in range(len(row)):
                cell_info = QTableWidgetItem(str(row[j]))
                cell_info.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.listInfo.setItem(i, j, QTableWidgetItem(cell_info))
            i = i + 1
            row = cursor.fetchone()


def main():
    app = QApplication(sys.argv)
    root = ListView()
    root.fill_table()
    root.show()
    app.exec()


if __name__ == '__main__':
    main()

cursor.close()
conn.close()
