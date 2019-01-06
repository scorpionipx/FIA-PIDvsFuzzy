import numpy as np
import pyqtgraph as pg
import serial
import struct
import sys
import threading

from time import sleep

from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication, QVBoxLayout, QPushButton, QTableWidget, \
    QTableWidgetItem, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


READ_FUZZY_TABLE_CMD = 10
WRITE_FUZZY_TABLE_CMD = 11
READ_PID_TABLE_CMD = 12
WRITE_PID_TABLE_CMD = 13


class Plotter(QWidget):
    """Plotter

    """
    TITLE = 'PID vs Fuzzy data analyzer'
    DATA_BUFFER_SIZE = 100

    def __init__(self):
        """Constructor

        """
        super(Plotter, self).__init__()
        self.init_ui()

        self.__connection__ = None
        self.connected = False

        self.ticks_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
        self.target_ticks_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
        self.power_supply_voltage_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
        self.data_buffer_0 = np.zeros(self.DATA_BUFFER_SIZE)
        self.data_buffer_1 = np.zeros(self.DATA_BUFFER_SIZE)

        self.target_ticks_plot_curve = pg.PlotCurveItem(pen='g')
        self.plot_widget.addItem(self.target_ticks_plot_curve)

        self.ticks_plot_curve = pg.PlotCurveItem(pen='r')
        self.plot_widget.addItem(self.ticks_plot_curve)

        self.power_supply_voltage_curve = pg.PlotCurveItem(pen='y')
        self.plot_widget.addItem(self.power_supply_voltage_curve)

        self.read_data_streaming = False

        self.plot_curve = pg.PlotCurveItem()
        self.plot_widget.addItem(self.plot_curve)
        self.update_plot()

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)

    def init_ui(self):
        self.setWindowTitle(self.TITLE)
        hbox = QVBoxLayout()
        tables_box = QHBoxLayout()
        self.setLayout(hbox)
        self.__load_widgets__()

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setYRange(0, 60, padding=0)
        self.plot_widget.setXRange(0, self.DATA_BUFFER_SIZE, padding=0)
        self.plot_widget.enableAutoRange('xy', False)

        hbox.addWidget(self.plot_widget)

        connection_buttons_box = QHBoxLayout()
        connection_buttons_box.addWidget(self.connect_button)
        connection_buttons_box.addWidget(self.connection_settings_button)
        connection_buttons_box.addWidget(self.data_streaming_button)
        connection_buttons_box.setAlignment(Qt.AlignLeading)
        hbox.addLayout(connection_buttons_box)

        fuzzy_buttons_box = QVBoxLayout()
        fuzzy_buttons_box.addWidget(self.read_fuzzy_table_button)
        fuzzy_buttons_box.addWidget(self.write_fuzzy_table_button)
        tables_box.addWidget(self.fuzzy_table)
        tables_box.addLayout(fuzzy_buttons_box)
        tables_box.addWidget(self.pid_table)
        pid_buttons_box = QVBoxLayout()
        pid_buttons_box.addWidget(self.read_pid_table_button)
        pid_buttons_box.addWidget(self.write_pid_table_button)
        tables_box.addLayout(pid_buttons_box)
        tables_box.setAlignment(Qt.AlignLeft)
        
        hbox.addLayout(tables_box)

        self.setGeometry(10, 10, 1000, 600)
        self.center()
        self.show()

    def fetch_usart_data(self):
        """fetch_usart_data

        :return:
        """
        if not self.connected:
            print("Not connected!")
            return

        self.send_usart_data(5)
        print("Data streaming command sent!")
        sleep(.01)

        while self.read_data_streaming:
            sleep(.005)

            if self.__connection__.in_waiting > 6:
                self.__connection__.read_all()

            elif self.__connection__.in_waiting < 6:
                # print("Not enough data")
                pass

            else:
                sync_data = ord(self.__connection__.read(1))
                if sync_data == 255:
                    self.target_ticks_data_buffer = np.roll(self.target_ticks_data_buffer, 1)
                    self.ticks_data_buffer = np.roll(self.ticks_data_buffer, 1)
                    self.power_supply_voltage_data_buffer = np.roll(self.power_supply_voltage_data_buffer, 1)
                    self.data_buffer_0 = np.roll(self.data_buffer_0, 1)
                    self.data_buffer_1 = np.roll(self.data_buffer_1, 1)

                    self.target_ticks_data_buffer[-1] = ord(self.__connection__.read())
                    self.ticks_data_buffer[-1] = ord(self.__connection__.read())
                    self.power_supply_voltage_data_buffer[-1] = ord(self.__connection__.read()) / 16
                    self.data_buffer_0[-1] = ord(self.__connection__.read())
                    self.data_buffer_1[-1] = ord(self.__connection__.read())

        print("Stopped usart data fetching!")

    def toggle_data_streaming(self):
        if self.read_data_streaming:
            self.read_data_streaming = False
            sleep(.1)
            self.target_ticks_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
            self.ticks_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
            self.power_supply_voltage_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
            self.data_buffer_0 = np.zeros(self.DATA_BUFFER_SIZE)
            self.data_buffer_1 = np.zeros(self.DATA_BUFFER_SIZE)
        else:
            self.read_data_streaming = True
            read_com_data_thread = threading.Thread(target=self.fetch_usart_data)
            read_com_data_thread.start()

    def __load_widgets__(self):
        """__load_widgets__

            Load widgets used in GUI.
        :return: None
        """
        self.__lw_fuzzy_table__()
        self.__lw_pid_table__()
        self.__lw_connection_buttons__()
        self.__lw_fuzzy_buttons__()
        self.__lw_pid_buttons__()
        
    def __lw_connection_buttons__(self):
        """__lw_connection_buttons__
        
            Load widgets used to handle PC to uC connection.
        :return: None
        """
        self.connect_button = QPushButton()
        self.connect_button.setText("CONNECT")
        self.connect_button.setToolTip("Establish connection between PC and uC")
        self.connect_button.setFixedSize(120, 40)
        self.connect_button.clicked.connect(self.connect)
        self.connect_button.show()
        
        self.connection_settings_button = QPushButton()
        self.connection_settings_button.setText("SETTINGS")
        self.connection_settings_button.setToolTip("Configure connection settings")
        self.connection_settings_button.setFixedSize(120, 40)
        self.connection_settings_button.clicked.connect(self.read_fuzzy_table)
        self.connection_settings_button.show()

        self.data_streaming_button = QPushButton()
        self.data_streaming_button.setText("DATA STREAMING")
        self.data_streaming_button.setToolTip("Toggle data streaming")
        self.data_streaming_button.setFixedSize(120, 40)
        self.data_streaming_button.clicked.connect(self.toggle_data_streaming)
        self.data_streaming_button.show()

    def connect(self):
        """connect

            Establish connection between PC and uC.
        :return: None
        """
        if self.connected:
            print("Disconnecting...")
            try:
                self.read_data_streaming = False
                sleep(.01)
                self.__connection__.close()
                self.__connection__ = None
                self.connected = False
                self.connect_button.setText("CONNECT")
                self.connect_button.setToolTip("Establish connection between PC and uC")
                print("Disconnected!")
                return
            except Exception as err:
                print("Failed to disconnect from EVB5.1! {}".format(err))
                return
        else:
            print("Connecting to EVB5.1...")
        try:
            self.__connection__ = serial.Serial('COM10', 38400, stopbits=serial.STOPBITS_TWO)
            self.connected = True
            print("Connected!")
            self.connect_button.setText("DISCONNECT")
            self.connect_button.setToolTip("Disestablish connection between PC and uC")
            return
        except Exception as err:
            self.connected = False
            print("Failed to connect to EVB5.1: {}".format(err))
            return

    def __lw_fuzzy_buttons__(self):
        """__lw_fuzzy_buttons__

        :return:
        """
        self.read_fuzzy_table_button = QPushButton()
        self.read_fuzzy_table_button.setText("READ")
        self.read_fuzzy_table_button.setToolTip("Read Fuzzy table used on control system (download from uC to PC)")
        self.read_fuzzy_table_button.setFixedSize(60, 60)
        self.read_fuzzy_table_button.clicked.connect(self.read_fuzzy_table)
        self.read_fuzzy_table_button.show()

        self.write_fuzzy_table_button = QPushButton()
        self.write_fuzzy_table_button.setText("WRITE")
        self.write_fuzzy_table_button.setToolTip("Write Fuzzy table in the control system (upload from PC to uC)")
        self.write_fuzzy_table_button.setFixedSize(60, 60)
        self.write_fuzzy_table_button.clicked.connect(self.write_fuzzy_table)
        self.write_fuzzy_table_button.show()

    def __lw_pid_buttons__(self):
        """__lw_pid_buttons__

        :return:
        """
        self.read_pid_table_button = QPushButton()
        self.read_pid_table_button.setText("READ")
        self.read_pid_table_button.setToolTip("Read PID table used on control system (download from uC to PC)")
        self.read_pid_table_button.setFixedSize(60, 60)
        self.read_pid_table_button.clicked.connect(self.read_pid_table)
        self.read_pid_table_button.show()

        self.write_pid_table_button = QPushButton()
        self.write_pid_table_button.setText("WRITE")
        self.write_pid_table_button.setToolTip("Write PID table in the control system (upload from PC to uC)")
        self.write_pid_table_button.setFixedSize(60, 60)
        self.write_pid_table_button.show()

    def update_plot(self):
        self.target_ticks_plot_curve.setData(self.target_ticks_data_buffer)
        self.ticks_plot_curve.setData(self.ticks_data_buffer)
        self.power_supply_voltage_curve.setData(self.power_supply_voltage_data_buffer)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def __lw_fuzzy_table__(self):
        """__lw_fuzzy_table__

            Load widgets used to hold PID table.
        :return: None
        """
        self.fuzzy_table = QTableWidget()
        self.fuzzy_table.setFixedWidth(480)
        self.fuzzy_table.setFixedHeight(125)
        self.fuzzy_table.setRowCount(5)
        self.fuzzy_table.setColumnCount(9)
        for i in range(5):
            for j in range(9):
                item = QTableWidgetItem("N/A")
                item.setTextAlignment(Qt.AlignCenter)
                self.fuzzy_table.setItem(i, j, item)
                self.fuzzy_table.setColumnWidth(j, 50)
            self.fuzzy_table.setRowHeight(i, 20)

        header_font = QFont()
        header_font.setBold(True)

        header = QTableWidgetItem()
        header.setText("NFM")
        header.setFont(header_font)
        self.fuzzy_table.setHorizontalHeaderItem(0, header)
        header = QTableWidgetItem()
        header.setText("NM")
        header.setFont(header_font)
        self.fuzzy_table.setHorizontalHeaderItem(1, header)
        header = QTableWidgetItem()
        header.setText("Nm")
        header.setFont(header_font)
        self.fuzzy_table.setHorizontalHeaderItem(2, header)
        header = QTableWidgetItem()
        header.setText("NFm")
        header.setFont(header_font)
        self.fuzzy_table.setHorizontalHeaderItem(3, header)
        header = QTableWidgetItem()
        header.setText("Z")
        header.setFont(header_font)
        self.fuzzy_table.setHorizontalHeaderItem(4, header)
        header = QTableWidgetItem()
        header.setText("PFm")
        header.setFont(header_font)
        self.fuzzy_table.setHorizontalHeaderItem(5, header)
        header = QTableWidgetItem()
        header.setText("Pm")
        header.setFont(header_font)
        self.fuzzy_table.setHorizontalHeaderItem(6, header)
        header = QTableWidgetItem()
        header.setText("PM")
        header.setFont(header_font)
        self.fuzzy_table.setHorizontalHeaderItem(7, header)
        header = QTableWidgetItem()
        header.setText("PFM")
        header.setFont(header_font)
        self.fuzzy_table.setHorizontalHeaderItem(8, header)

        header = QTableWidgetItem()
        header.setText("NM")
        header.setFont(header_font)
        self.fuzzy_table.setVerticalHeaderItem(0, header)
        header = QTableWidgetItem()
        header.setText("Nm")
        header.setFont(header_font)
        self.fuzzy_table.setVerticalHeaderItem(1, header)
        header = QTableWidgetItem()
        header.setText("Z")
        header.setFont(header_font)
        self.fuzzy_table.setVerticalHeaderItem(2, header)
        header = QTableWidgetItem()
        header.setText("Pm")
        header.setFont(header_font)
        self.fuzzy_table.setVerticalHeaderItem(3, header)
        header = QTableWidgetItem()
        header.setText("PM")
        header.setFont(header_font)
        self.fuzzy_table.setVerticalHeaderItem(4, header)

        self.fuzzy_table.move(0, 0)

    def __lw_pid_table__(self):
        """__lw_pid_table__

            Load widgets used to hold PID table.
        :return: None
        """
        self.pid_table = QTableWidget()
        self.pid_table.setFixedHeight(125)
        self.pid_table.setFixedWidth(90)
        self.pid_table.setRowCount(3)
        self.pid_table.setColumnCount(1)
        self.pid_table.setColumnWidth(0, 70)
        for i in range(3):
            item = QTableWidgetItem("N/A")
            item.setTextAlignment(Qt.AlignCenter)
            self.pid_table.setItem(i, 0, item)
            self.pid_table.setRowHeight(i, 33)
        self.pid_table.move(0, 0)

        header_font = QFont()
        header_font.setBold(True)

        header = QTableWidgetItem()
        header.setText("PID")
        header.setFont(header_font)
        self.pid_table.setHorizontalHeaderItem(0, header)

        header = QTableWidgetItem()
        header.setText("P")
        header.setFont(header_font)
        self.pid_table.setVerticalHeaderItem(0, header)

        header = QTableWidgetItem()
        header.setText("I")
        header.setFont(header_font)
        self.pid_table.setVerticalHeaderItem(1, header)

        header = QTableWidgetItem()
        header.setText("D")
        header.setFont(header_font)
        self.pid_table.setVerticalHeaderItem(2, header)

    def write_fuzzy_table(self):
        """write_fuzzy_table

        :return:
        """
        self.send_usart_data(WRITE_FUZZY_TABLE_CMD)
        received = self.__connection__.read(1)
        print("Response: {}".format(received))

    def read_fuzzy_table(self):
        """read_fuzzy_table

            Read Fuzzy table used on control system.
        :return: None
        """

        if not self.connected:
            print("Not connected to EVB5.1!")
            return

        self.send_usart_data(READ_FUZZY_TABLE_CMD)

        while self.__connection__.in_waiting < 90:
            pass

        while self.__connection__.in_waiting > 90:
            self.__connection__.read(self.__connection__.in_waiting - 90)

        for i in range(5):
            for j in range(9):
                value = self.__connection__.read(2)
                value = struct.unpack('>h', value)[0]
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.fuzzy_table.setItem(i, j, item)

        print("Fuzy table transmitted!")

        self.__connection__.read_all()

    def read_pid_table(self):
        """read_pid_table

            Read pid constants used on control system.
        :return: None
        """

        if not self.connected:
            print("Not connected to EVB5.1!")
            return

        self.send_usart_data(READ_PID_TABLE_CMD)

        while self.__connection__.in_waiting < 12:
            pass

        while self.__connection__.in_waiting > 12:
            print("Extra bytes received: {}".format(self.__connection__.in_waiting))
            self.__connection__.read(self.__connection__.in_waiting - 12)

        for i in range(3):
            value = self.__connection__.read(4)
            # print(value)
            value = struct.unpack('f', value)[0]
            item = QTableWidgetItem(str(value)[:8])
            item.setTextAlignment(Qt.AlignCenter)
            self.pid_table.setItem(0, i, item)
        print("PID table transmitted!")

        self.__connection__.read_all()

    def send_usart_data(self, data):
        """

        :param data: data to be sent
        :type data: int
        :return:
        """
        bytes_sent = self.__connection__.write(bytes([data]))
        # print("Bytes sent: {}".format(bytes_sent))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('PIDvsFuzzy')
    ex = Plotter()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
