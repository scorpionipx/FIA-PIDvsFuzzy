import numpy as np
import pyqtgraph as pg
import serial
import struct
import sys
import threading

from time import sleep

from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication, QVBoxLayout, QPushButton, QTableWidget, \
    QTableWidgetItem, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


STOP_CONTROL_LOOP_CMD = 0
INCREASE_TARGET_TICKS_CMD = 1
DECREASE_TARGET_TICKS_CMD = 2
SELECT_PID_CONTROL_LOOP_CMD = 3
SELECT_FUZZY_CONTROL_LOOP_CMD = 4
TOGGLE_DATA_STREAMING_CMD = 5
READ_FUZZY_TABLE_CMD = 10
WRITE_FUZZY_TABLE_CMD = 11
READ_PID_TABLE_CMD = 12
WRITE_PID_TABLE_CMD = 13


class Plotter(QWidget):
    """Plotter

    """
    TITLE = 'PID vs Fuzzy data analyzer'
    DATA_BUFFER_SIZE = 1000

    def __init__(self):
        """Constructor

        """
        super(Plotter, self).__init__()
        self.init_ui()

        self.__connection__ = None
        self.connected = False
        self.__updating_usart_data__ = False
        self.__freeze_plotter__ = False

        self.ticks_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
        self.target_ticks_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
        self.power_supply_voltage_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
        self.algorithm_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
        self.algorithm_start_flag_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)

        self.target_ticks_plot_curve = pg.PlotCurveItem(pen='g')
        self.plot_widget.addItem(self.target_ticks_plot_curve)

        self.ticks_plot_curve = pg.PlotCurveItem(pen='r')
        self.plot_widget.addItem(self.ticks_plot_curve)

        self.power_supply_voltage_curve = pg.PlotCurveItem(pen='y')
        self.plot_widget.addItem(self.power_supply_voltage_curve)

        self.algorithm_start_flag_curve = pg.PlotCurveItem(pen='w')
        self.plot_widget.addItem(self.algorithm_start_flag_curve)

        self.read_data_streaming = False

        self.plot_curve = pg.PlotCurveItem()
        self.plot_widget.addItem(self.plot_curve)
        self.update_plot()

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)

    def init_ui(self):
        self.setWindowTitle(self.TITLE)
        hbox = QVBoxLayout()
        tables_box = QHBoxLayout()
        self.setLayout(hbox)
        self.__load_widgets__()

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setYRange(-1, 35, padding=0)
        self.plot_widget.setXRange(0, self.DATA_BUFFER_SIZE, padding=0)
        self.plot_widget.enableAutoRange('xy', False)

        hbox.addWidget(self.plot_widget)

        connection_buttons_box = QHBoxLayout()
        connection_buttons_box.addWidget(self.connect_button)
        connection_buttons_box.addWidget(self.connection_settings_button)
        connection_buttons_box.addWidget(self.data_streaming_button)
        connection_buttons_box.addWidget(self.freeze_plotter_button)
        connection_buttons_box.setAlignment(Qt.AlignLeading)
        legend_box_0 = QVBoxLayout()
        legend_box_0.setAlignment(Qt.AlignCenter)
        legend_box_0.addWidget(self.legend_red_label)
        legend_box_0.addWidget(self.legend_green_label)
        legend_box_1 = QVBoxLayout()
        legend_box_1.setAlignment(Qt.AlignCenter)
        legend_box_1.addWidget(self.legend_yellow_label)
        legend_box_1.addWidget(self.legend_white_label)
        connection_buttons_box.addLayout(legend_box_0)
        connection_buttons_box.addLayout(legend_box_1)
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

        control_loop_box = QHBoxLayout()
        control_loop_target_box = QVBoxLayout()
        control_loop_target_box.setAlignment(Qt.AlignVCenter)
        control_loop_target_box.addWidget(self.stop_control_loop_button)
        control_loop_target_box.addWidget(self.increase_control_loop_target_ticks_button)
        control_loop_target_box.addWidget(self.decrease_control_loop_target_ticks_button)
        control_loop_box.addLayout(control_loop_target_box)
        control_loop_box.addWidget(self.target_ticks_label)
        control_loop_select_algorithm = QVBoxLayout()
        control_loop_select_algorithm.addWidget(self.control_loop_pid_button)
        control_loop_select_algorithm.addWidget(self.control_loop_fuzzy_button)
        control_loop_box.addLayout(control_loop_select_algorithm)

        tables_box.addLayout(control_loop_box)
        
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
                    self.__updating_usart_data__ = True
                    self.target_ticks_data_buffer = np.roll(self.target_ticks_data_buffer, 1)
                    self.ticks_data_buffer = np.roll(self.ticks_data_buffer, 1)
                    self.power_supply_voltage_data_buffer = np.roll(self.power_supply_voltage_data_buffer, 1)

                    self.algorithm_data_buffer = np.roll(self.algorithm_data_buffer, 1)
                    self.algorithm_start_flag_data_buffer = np.roll(self.algorithm_start_flag_data_buffer, 1)

                    self.target_ticks_data_buffer[0] = ord(self.__connection__.read())
                    self.ticks_data_buffer[0] = ord(self.__connection__.read())
                    self.power_supply_voltage_data_buffer[0] = ord(self.__connection__.read()) / 16
                    self.algorithm_data_buffer[0] = ord(self.__connection__.read())
                    self.algorithm_start_flag_data_buffer[0] = ord(self.__connection__.read())
                    self.__updating_usart_data__ = False

        print("Stopped usart data fetching!")

    def toggle_data_streaming(self):
        if self.read_data_streaming:
            self.read_data_streaming = False
            sleep(.1)
            self.target_ticks_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
            self.ticks_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
            self.power_supply_voltage_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
            self.algorithm_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
            self.algorithm_start_flag_data_buffer = np.zeros(self.DATA_BUFFER_SIZE)
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
        self.__lw_control_loop_buttons__()

    def __lw_control_loop_buttons__(self):
        """__lw_control_loop_buttons__

        :return: None
        """
        self.stop_control_loop_button = QPushButton()
        self.stop_control_loop_button.setText("STOP")
        self.stop_control_loop_button.setToolTip("Stop control loop")
        self.stop_control_loop_button.setFixedSize(38, 38)
        self.stop_control_loop_button.clicked.connect(self.stop_control_loop)
        self.stop_control_loop_button.show()

        self.increase_control_loop_target_ticks_button = QPushButton()
        self.increase_control_loop_target_ticks_button.setText("+")
        self.increase_control_loop_target_ticks_button.setToolTip("Increase control loop target ticks")
        self.increase_control_loop_target_ticks_button.setFixedSize(38, 38)
        self.increase_control_loop_target_ticks_button.clicked.connect(self.increase_target_ticks)
        self.increase_control_loop_target_ticks_button.show()

        self.decrease_control_loop_target_ticks_button = QPushButton()
        self.decrease_control_loop_target_ticks_button.setText("-")
        self.decrease_control_loop_target_ticks_button.setToolTip("Decrease control loop target ticks")
        self.decrease_control_loop_target_ticks_button.setFixedSize(38, 38)
        self.decrease_control_loop_target_ticks_button.clicked.connect(self.decrease_target_ticks)
        self.decrease_control_loop_target_ticks_button.show()

        label_font = QFont()
        # label_font.setBold(True)
        label_font.setPointSize(70)

        self.target_ticks_label = QLabel()
        self.target_ticks_label.setFrameShape(QFrame.Panel)
        self.target_ticks_label.setFont(label_font)
        self.target_ticks_label.setAlignment(Qt.AlignCenter)
        self.target_ticks_label.setText("0")
        self.target_ticks_label.setFixedSize(120, 120)
        self.target_ticks_label.show()

        self.control_loop_pid_button = QPushButton()
        self.control_loop_pid_button.setText("PID")
        self.control_loop_pid_button.setToolTip("Select PID control loop")
        self.control_loop_pid_button.setFixedSize(100, 58)
        self.control_loop_pid_button.clicked.connect(self.select_pid_control_loop)
        self.control_loop_pid_button.show()

        self.control_loop_fuzzy_button = QPushButton()
        self.control_loop_fuzzy_button.setText("Fuzzy")
        self.control_loop_fuzzy_button.setToolTip("Select Fuzzy control loop")
        self.control_loop_fuzzy_button.setFixedSize(100, 58)
        self.control_loop_fuzzy_button.clicked.connect(self.select_fuzzy_control_loop)
        self.control_loop_fuzzy_button.show()

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

        self.freeze_plotter_button = QPushButton()
        self.freeze_plotter_button.setText("FREEZE DATA")
        self.freeze_plotter_button.setToolTip("Stop updating plotter")
        self.freeze_plotter_button.setFixedSize(120, 40)
        self.freeze_plotter_button.clicked.connect(self.freeze_plotter)
        self.freeze_plotter_button.show()

        self.legend_red_label = QLabel()
        self.legend_red_label.setStyleSheet("background-color: red")
        self.legend_red_label.setAlignment(Qt.AlignCenter)
        self.legend_red_label.setText("CURRENT SPEED")
        self.legend_red_label.setFixedSize(150, 12)
        self.legend_red_label.show()

        self.legend_green_label = QLabel()
        self.legend_green_label.setStyleSheet("background-color: green")
        self.legend_green_label.setAlignment(Qt.AlignCenter)
        self.legend_green_label.setText("TARGET SPEED")
        self.legend_green_label.setFixedSize(150, 12)
        self.legend_green_label.show()

        self.legend_yellow_label = QLabel()
        self.legend_yellow_label.setStyleSheet("background-color: yellow")
        self.legend_yellow_label.setAlignment(Qt.AlignCenter)
        self.legend_yellow_label.setText("POWER SUPPLY VOLTAGE")
        self.legend_yellow_label.setFixedSize(150, 12)
        self.legend_yellow_label.show()

        self.legend_white_label = QLabel()
        self.legend_white_label.setStyleSheet("background-color: white")
        self.legend_white_label.setAlignment(Qt.AlignCenter)
        self.legend_white_label.setText("ALGORITHM STARTED")
        self.legend_white_label.setFixedSize(150, 12)
        self.legend_white_label.show()

    def freeze_plotter(self):
        """

        :return:
        """
        if self.__freeze_plotter__:
            self.__freeze_plotter__ = False
            self.freeze_plotter_button.setText("FREEZE DATA")
        else:
            self.__freeze_plotter__ = True
            self.freeze_plotter_button.setText("UNFREEZE DATA")

    def stop_control_loop(self):
        """stop_control_loop

        :return:
        """
        if not self.connected:
            print("Not connected!")
            return
        self.send_usart_data(STOP_CONTROL_LOOP_CMD)

    def increase_target_ticks(self):
        """increase_target_ticks

        :return:
        """
        if not self.connected:
            print("Not connected!")
            return
        self.send_usart_data(INCREASE_TARGET_TICKS_CMD)

    def decrease_target_ticks(self):
        """decrease_target_ticks

        :return:
        """
        if not self.connected:
            print("Not connected!")
            return
        self.send_usart_data(DECREASE_TARGET_TICKS_CMD)

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
        if self.__freeze_plotter__:
            return

        while self.__updating_usart_data__:
            pass

        self.target_ticks_plot_curve.setData(self.target_ticks_data_buffer)
        self.target_ticks_label.setText(str(int(self.target_ticks_data_buffer[0])))
        self.ticks_plot_curve.setData(self.ticks_data_buffer)
        self.power_supply_voltage_curve.setData(self.power_supply_voltage_data_buffer)
        self.algorithm_start_flag_curve.setData(self.algorithm_start_flag_data_buffer)
        if self.algorithm_data_buffer[0] == 0:
            self.control_loop_pid_button.setStyleSheet("background-color: none")
            self.control_loop_fuzzy_button.setStyleSheet("background-color: none")
            pass
        elif self.algorithm_data_buffer[0] == 1:
            self.control_loop_pid_button.setStyleSheet("background-color: green")
            self.control_loop_fuzzy_button.setStyleSheet("background-color: none")
            pass
        elif self.algorithm_data_buffer[0] == 2:
            self.control_loop_pid_button.setStyleSheet("background-color: none")
            self.control_loop_fuzzy_button.setStyleSheet("background-color: green")
            pass
        else:
            self.control_loop_pid_button.setStyleSheet("background-color: red")
            self.control_loop_fuzzy_button.setStyleSheet("background-color: red")

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

    def select_pid_control_loop(self):
        """

        :return:
        """
        if not self.connected:
            print("Not connected to EVB5.1!")
            return

        self.send_usart_data(SELECT_PID_CONTROL_LOOP_CMD)

    def select_fuzzy_control_loop(self):
        """

        :return:
        """
        if not self.connected:
            print("Not connected to EVB5.1!")
            return

        self.send_usart_data(SELECT_FUZZY_CONTROL_LOOP_CMD)



def main():
    app = QApplication(sys.argv)
    app.setApplicationName('PIDvsFuzzy')
    ex = Plotter()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
