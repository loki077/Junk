###-----------------------------------------------------------------
#   File        :   esc_log_analysis.py
#   Description :   
#   Author      :   Lokesh Ramina
#   Notes       :   --
#   Date        :   13/1/2023
#   Rev History :   V 1.0
#   COPYRIGHT NOTICE: (c) 2022 Carbonix.  All rights reserved.
#   link            : 
###-----------------------------------------------------------------

#Need to add the below code in AP_gps_.cpp
#GCS_SEND_TEXT(MAV_SEVERITY_CRITICAL, "GPS_LOG,%u,%u,%u,%u,%f  ",t.last_fix_time_ms,t.last_message_time_ms,t.delta_time_ms,t.delayed_count,t.average_delta_ms);
###-----------------------------------------------------------------
#   File        :   esc_pkt_scan.py
#   Description :   test script to check if all CAN GPS nodes are producing Fix2 frames at the expected rate
#   Author      :   Lokesh Ramina
#   Notes       :   --
#   Date        :   12/12/2022
#   Rev History :   V 1.0
#   COPYRIGHT NOTICE: (c) 2022 Carbonix.  All rights reserved.
#   link            https://dronecan.github.io/Implementations/Pydronecan/Tutorials/2._Basic_usage/
#                   https://www.guru99.com/pyqt-tutorial.html
#                   https://realpython.com/python-pyqt-layout/
###-----------------------------------------------------------------

# from __future__ import annotations
from typing import *
from PyQt5.QtWidgets import QLabel, QDialog, QSpinBox, QGridLayout, QGroupBox , QApplication, QPushButton, QLineEdit, QProgressBar, QFileDialog,QComboBox
from PyQt5.QtCore import QTimer, Qt, QDateTime


# importing pyqtgraph as pg
import pyqtgraph as pg

from logging import getLogger
import pandas as pd

from matplotlib.backends.backend_qt5agg import FigureCanvas
import matplotlib.figure as mpl_fig
import matplotlib.animation as anim

from pathlib import Path
import fnmatch

import dronecan
from pymavlink import mavutil

#can be excluded
import sys, os
import glob
from argparse import ArgumentParser

__all__ = 'PANEL_NAME', 'spawn', 'get_icon'

PANEL_NAME = 'ESC SITL'

RUNNING_ON_LINUX = 'linux' in sys.platform.lower()

logger = getLogger(__name__)

_singleton = None
class MyFigureCanvas(FigureCanvas, anim.FuncAnimation):
    '''
    This is the FigureCanvas in which the live plot is drawn.

    '''
    def __init__(self, x_len:int, y_range:list, interval:int,  title:str ,x_label:str, y_label:str) -> None:
        '''
        :param x_len:       The nr of data points shown in one plot.
        :param y_range:     Range on y-axis.
        :param interval:    Get a new datapoint every .. milliseconds.

        '''
        FigureCanvas.__init__(self, mpl_fig.Figure())
        # Range settings
        self._x_len_ = x_len
        self._y_range_ = y_range

        # Store two lists _x_ and _y_
        self.x = list(range(0, x_len))
        self.y = [0] * x_len

        # Store a figure and ax
        self._ax_ = self.figure.subplots()
        self._ax_.set_xlabel(x_label)
        self._ax_.set_ylabel(y_label)
        self._ax_.set_title(title)
        self._ax_.set_ylim(ymin=self._y_range_[0], ymax=self._y_range_[1])
        self._line_, = self._ax_.plot(self.x, self.y)

        # Call superclass constructors
        anim.FuncAnimation.__init__(self, self.figure, self._update_canvas_, fargs=(self.y,), interval=interval, blit=True)
        return
    def add_data(self, val):
        self.y.append(val)

    def _update_canvas_(self, i, y) -> None:
        '''
        This function gets called regularly by the timer.

        '''
        self.y = self.y[-self._x_len_:]                        # Truncate list _y_
        self._ax_.set_ylim(ymin=min(self.y), ymax= 10 if max(self.y) < 10 else max(self.y))
        self._line_.set_ydata(self.y)
        return self._line_,

class ESCLogAnalysis(QDialog):
    DEFAULT_INTERVAL = 0.1

    CMD_BIT_LENGTH = dronecan.get_dronecan_data_type(dronecan.uavcan.equipment.esc.RawCommand().cmd).value_type.bitlen
    CMD_MAX = 2 ** (CMD_BIT_LENGTH - 1) - 1
    CMD_MIN = -(2 ** (CMD_BIT_LENGTH - 1))

    def __init__(self, node):
        super(ESCLogAnalysis, self).__init__()
        self.setWindowTitle('GPS Scan')
        self.setAttribute(Qt.WA_DeleteOnClose)              # This is required to stop background timers!
        self._ifaces = self.list_ifaces()
        self.data_key = {"last_fix_time_ms":0,"last_message_time_ms":0,"delta_time_ms":0,"delayed_count":0,"average_delta_ms":0, "lagged_sample_count":0}
        self.ts = []
        self.telem_rpm_ls = []
        self.telem_volt_ls = []
        self.telem_curr_ls = []
        self.telem_temp_ls = []
        self.telem_error_ls = []
        self.thr_out_ls = []
        self.arm_requested = False
        self.thr_out_list = []
        self.thr_out_list_pt = 0
        #create File
        self.col_names = ['Time Stamp',
             'Username',
             'Email',
             'Motor Details',
             'Props Details',
             'ESC Details',
             'CPN Dev ID',
             'Log File',
             'Motor Selection',
             'Ramp Modification',
             'Run Time',
             'Test Start TS',
             'Test End TS',
             'Final Status',
             'Telem Log File Name'
            ]
        self.telem_col_names = ['Time Stamp',
             'Throttle Out',
             'RPM',
             'Voltage',
             'Current',
             'Error',
             'Temperature',
            ]

        time = QDateTime.currentDateTime()
        time_display = time.toString('yyyyMMdd hhmmss dddd')
        self.telem_log_file_name =  self.resource_path("esc_log_analysis_master"+time_display+".csv")
        print(self.telem_log_file_name)
        self.telem_log_file = pd.DataFrame([], columns=self.telem_col_names)
        self.telem_log_file.to_csv(self.telem_log_file_name)
        print("Telem Log File Created")

        self.master_file_name = self.resource_path("esc_log_analysis_master.csv")
        self.master_file_path = Path(self.master_file_name)

        if self.master_file_path.exists():
            self.master_file = pd.read_csv(self.master_file_name)
            print("Master log File Open")
        else:
            self.master_file = pd.DataFrame([], columns=self.col_names)
            self.master_file.to_csv(self.master_file_name)
            print("Master log File Created")

        #drone can parameter
        # self._node = node        
        self._subscriber_handle = None

        #timmer parameter
        self.start_time = None
        self.end_time = None

        #layout
        layout = QGridLayout(self)
        
        self._node_spin_timer = QTimer(self)
        self._node_spin_timer.timeout.connect(self._spin_node)
        self._node_spin_timer.setSingleShot(False)
        self._node_spin_timer.stop()

        #Operator Details
        self.user_name = QLineEdit(self)
        self.user_email = QLineEdit(self)
        self.prop_details = QLineEdit(self)
        self.motor_details = QLineEdit(self)
        self.esc_details = QLineEdit(self)

        self.cpn_dev_id = QSpinBox(self)
        self.cpn_dev_id.setMaximum(125)
        self.cpn_dev_id.setMinimum(1)
        self.cpn_dev_id.setValue(11)

        self.log_file_path = QLineEdit(self)
        self.file_load_btn = QPushButton('Browse Log')
        self.file_load_btn.clicked.connect(self.open)
        self.load_log = QPushButton('Load Log')
        self.load_log.clicked.connect(self.load_log_prc)
        self.log_scan_scan_progress = QProgressBar(self)

        self.prop_details.setText("29*9.5 2 Blade Tmotor")
        self.motor_details.setText("V10 Tmotor")
        self.esc_details.setText("HV Pro APD")

        self.user_detail_group = QGroupBox('User Details', self)
        user_detail_layout = QGridLayout(self)
        user_detail_layout.addWidget(QLabel('User Name  :', self),      0,0)
        user_detail_layout.addWidget(self.user_name,                    0,1)
        user_detail_layout.addWidget(QLabel('User Email :', self),      1,0)
        user_detail_layout.addWidget(self.user_email,                   1,1)
        user_detail_layout.addWidget(QLabel('Prop Details :', self),    2,0)
        user_detail_layout.addWidget(self.prop_details,                 2,1)
        user_detail_layout.addWidget(QLabel('Motor Details :', self),   3,0)
        user_detail_layout.addWidget(self.motor_details,                3,1)
        user_detail_layout.addWidget(QLabel('ESC Details :', self),     4,0)
        user_detail_layout.addWidget(self.esc_details,                  4,1)
        user_detail_layout.addWidget(QLabel('CPN Dev ID :', self),      5,0)
        user_detail_layout.addWidget(self.cpn_dev_id,                   5,1)
        user_detail_layout.addWidget(self.file_load_btn,                6,0)
        user_detail_layout.addWidget(self.log_file_path,                     6,1)
        user_detail_layout.addWidget(self.load_log,                     7,0,1,2)
        user_detail_layout.addWidget(self.log_scan_scan_progress,       8,0,1,2)
        self.user_detail_group.setLayout(user_detail_layout)

        # Config Value param  

        self.motor_selection = QSpinBox(self)
        self.motor_selection.setMaximum(4)
        self.motor_selection.setMinimum(1)
        self.motor_selection.setValue(1)    

        self.run_time = QSpinBox(self)
        self.run_time.setMaximum(10000)
        self.run_time.setMinimum(0)
        self.run_time.setValue(0)

        self.ramp_prct_mod = QSpinBox(self)
        self.ramp_prct_mod.setMaximum(100)
        self.ramp_prct_mod.setMinimum(-100)
        self.ramp_prct_mod.setValue(0)

        self.connect_btn = QPushButton('Connect')
        self.connect_btn.clicked.connect(self.connect_can)

        self.serial_com_box = QComboBox()    
        for z in self._ifaces:
            self.serial_com_box.addItem(z)   

        self.config_group = QGroupBox('Configure Parameter', self)
        config_layout = QGridLayout(self)
        config_layout.addWidget(QLabel('Serail Port         :', self),      0,0)
        config_layout.addWidget(self.serial_com_box,                        0,0)
        config_layout.addWidget(QLabel('Motor Selection     :', self),      1,0)
        config_layout.addWidget(self.motor_selection,                       1,1)
        config_layout.addWidget(QLabel('Run Time(sec)       :', self),      2,0)
        config_layout.addWidget(self.run_time,                              2,1)
        config_layout.addWidget(QLabel('Ramp Modification % :', self),      3,0)
        config_layout.addWidget(self.ramp_prct_mod,                         3,1)
        config_layout.addWidget(self.connect_btn,                           4,0,1,2)
        self.config_group.setLayout(config_layout)
        self.config_group.setEnabled(False)

        # Live value param
        self._node_id           = QLabel('0', self)
        self._thr_value_out     = QLabel('0', self)
        self._tele_rpm      = QLabel('0', self)
        self._tele_volt     = QLabel('0', self)
        self._tele_curr     = QLabel('0', self)
        self._tele_temp     = QLabel('0', self)
        self._tele_status   = QLabel('0', self)
        self._arm_status    = QLabel('0', self)


        self.scan_value_group = QGroupBox('Live Value', self)
        scan_value_layout = QGridLayout(self)
        scan_value_layout.addWidget(QLabel('Node Id     :', self),      0,0)
        scan_value_layout.addWidget(self._node_id,                      0,1)
        scan_value_layout.addWidget(QLabel('Thr Val Out :', self),      1,0)
        scan_value_layout.addWidget(self._thr_value_out,                1,1)
        scan_value_layout.addWidget(QLabel('RPM         :', self),      2,0)
        scan_value_layout.addWidget(self._tele_rpm,                     2,1)
        scan_value_layout.addWidget(QLabel('Voltage     :', self),      3,0)
        scan_value_layout.addWidget(self._tele_volt,                    3,1)
        scan_value_layout.addWidget(QLabel('Current     :', self),      4,0)
        scan_value_layout.addWidget(self._tele_curr,                    4,1)
        scan_value_layout.addWidget(QLabel('Temperature :', self),      5,0)
        scan_value_layout.addWidget(self._tele_temp,                    5,1)
        scan_value_layout.addWidget(QLabel('Error Status:', self),      6,0)
        scan_value_layout.addWidget(self._tele_status,                  6,1)
        scan_value_layout.addWidget(QLabel('ARM         :', self),      7,0)
        scan_value_layout.addWidget(self._arm_status,                   7,1)
        self.scan_value_group.setLayout(scan_value_layout)
        self.scan_value_group.setEnabled(False)

        #start scan
        self.arm_timer_label=QLabel('Start time')
        self.disarm_timer_label=QLabel('End Time')
        self.current_timer_label=QLabel('Time')
        self.time_elapsed_label=QLabel('0')
        self.arm_btn = QPushButton('ARM')
        self.disarm_btn   = QPushButton('DISARM')
        self.generate_report_button = QPushButton('Generate Report')

        self.timer = QTimer()
        self.timer.timeout.connect(self.show_time)
        self.arm_btn.clicked.connect(self.arm_timer)
        self.disarm_btn.clicked.connect(self.disarm_timer)
        self.generate_report_button.clicked.connect(self.file_save)
        self.scan_progress = QProgressBar(self)
        self.timer.stop()

        self.scan_group = QGroupBox('RUN ESC', self)
        scan_layout = QGridLayout(self)
        scan_layout.addWidget(QLabel('Time', self),         0,0)
        scan_layout.addWidget(self.current_timer_label,     0,1)
        scan_layout.addWidget(QLabel('Start Time', self),   1,0)
        scan_layout.addWidget(self.arm_timer_label,         1,1)
        scan_layout.addWidget(QLabel('Stop Time', self),    2,0)
        scan_layout.addWidget(self.disarm_timer_label,      2,1)
        scan_layout.addWidget(QLabel('Time elapsed', self), 3,0)
        scan_layout.addWidget(self.time_elapsed_label,      3,1)
        scan_layout.addWidget(self.arm_btn,                 4,0)
        scan_layout.addWidget(self.disarm_btn,              4,1)
        scan_layout.addWidget(self.scan_progress,           5,0,1,2)
        self.scan_group.setLayout(scan_layout)
        self.scan_group.setEnabled(False)

        #Generate Report 
        self.thr_out_fig = MyFigureCanvas(x_len=750, y_range=[0, 100], interval=20, title = "Throttle Out" ,x_label = "time", y_label = "PWM")
        self.rpm_fig = MyFigureCanvas(x_len=750, y_range=[0, 100], interval=20, title = "RPM" ,x_label = "time", y_label = "rpm")
        self.volt_fig = MyFigureCanvas(x_len=750, y_range=[0, 100], interval=20, title = "Voltage" ,x_label = "time", y_label = "V")
        self.curr_fig = MyFigureCanvas(x_len=750, y_range=[0, 100], interval=20, title = "Current" ,x_label = "time", y_label = "A")
        self.temp_fig = MyFigureCanvas(x_len=750, y_range=[0, 100], interval=20, title = "Temperature" ,x_label = "time", y_label = "degC")

        self.user_detail_group.setMaximumHeight(400)
        self.config_group.setMaximumHeight(200)
        self.scan_value_group.setMaximumHeight(400)
        self.scan_group.setMaximumHeight(200)
        #Final Value
        layout.addWidget(self.user_detail_group ,0,0,2,1)
        layout.addWidget(self.config_group      ,0,2,1,2)
        layout.addWidget(self.scan_value_group  ,0,1,2,1)
        layout.addWidget(self.scan_group        ,1,2,1,2)
        layout.addWidget(self.thr_out_fig       ,2,0,1,1)
        layout.addWidget(self.rpm_fig           ,2,1,1,1)
        layout.addWidget(self.volt_fig          ,2,2,1,1)
        layout.addWidget(self.temp_fig          ,2,3,1,1)


        self.setLayout(layout)
        # self.resize(600 if (self.minimumWidth()< 300) else self.minimumWidth(), self.minimumHeight())

        #connect 
        self.user_name.textChanged.connect(self.on_user_detail_changed)
        self.user_email.textChanged.connect(self.on_user_detail_changed)
        self.show()
        return
    
    def match_type(self, mtype, patterns):
        '''return True if mtype matches pattern'''
        for p in patterns:
            if fnmatch.fnmatch(mtype, p):
                return True
        return False

    def list_ifaces(self):
        """Returns dictionary, where key is description, value is the OS assigned name of the port"""
        if RUNNING_ON_LINUX:
            # Linux system
            ifaces = glob.glob('/dev/serial/by-id/*')
            try:
                ifaces = list(sorted(ifaces,
                                    key=lambda s: not ('zubax' in s.lower() and 'babel' in s.lower())))
            except Exception:
                logger.warning('Sorting failed', exc_info=True)

            out = OrderedDict()
            for x in ifaces:
                out[x] = x

            return out
        else:
            # Windows, Mac, whatever
            from PyQt5 import QtSerialPort

            out = OrderedDict()
            for port in QtSerialPort.QSerialPortInfo.availablePorts():
                if sys.platform == 'darwin':
                    if 'tty' in port.systemLocation():
                        out[port.systemLocation()] = port.systemLocation()
                else:
                    out[port.description()] = port.systemLocation()

        return out
    
    #
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path,relative_path)

    #load log
    def load_log_prc(self):
        self.load_log.setEnabled(False)
        filename = self.log_file_path.text()
        last_timestamp = None
        types = ["ARM", "RCOU", "ESC"]
        available_types = set()
        fields = ['timestamp', 'mavpackettype', 'TimeUS', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'Instance', 'RPM_1', 'RawRPM_1', 'Volt_1', 'Curr_1', 'Temp_1', 'CTot_1', 'MotTemp_1', 'Err_1','RPM_2', 'RawRPM_2', 'Volt_2', 'Curr_2', 'Temp_2', 'CTot_2', 'MotTemp_2', 'Err_2','RPM_3', 'RawRPM_3', 'Volt_3', 'Curr_3', 'Temp_3', 'CTot_3', 'MotTemp_3', 'Err_3','RPM_4', 'RawRPM_4', 'Volt_4', 'Curr_4', 'Temp_4', 'CTot_4', 'MotTemp_4', 'Err_4']

        print(filename)
        # Track types found
        available_types = set()
        if Path(filename).exists():
            self.log_scan_scan_progress.setValue(10)
            ext = os.path.splitext(filename)[1]
            isbin = ext in ['.bin', '.BIN', '.px4log']
            islog = ext in ['.log', '.LOG'] # NOTE: "islog" does not mean a tlog
            istlog = ext in ['.tlog', '.TLOG']
            iscsv = ext in ['.csv', '.CSV']
            arm_state = 0
            rcou = 0
            count = 0
            if isbin:
                self.log_scan_scan_progress.setValue(20)
                self.mlog = mavutil.mavlink_connection(filename,dialect="ardupilotmega")
                # for DF logs pre-calculate types list
                match_types=None
                if hasattr(self.mlog, 'name_to_id'):
                    for k in self.mlog.name_to_id.keys():
                        if self.match_type(k, types):
                            if match_types is None:
                                match_types = []
                            match_types.append(k)
                
                if match_types is None:
                    print("Data Not found")
                    self.log_scan_scan_progress.setValue(0)
                    self.load_log.setEnabled(True)
                    return "Data Not found" 

                # match_types.append("FMT")

                self.log_scan_scan_progress.setValue(30)
                print(match_types)
                print("Log File Open")

                self.processed_df = pd.DataFrame([], columns=fields)
                self.processed_df.to_csv(filename+".csv",index=False)

                self.log_scan_scan_progress.setValue(50)
                while True:
                    if args.max_data_size != None:
                        count = count+1
                        if count > args.max_data_size:
                            self.log_scan_scan_progress.setValue(90)
                            self.processed_df.to_csv(filename+".csv", index=False)
                            self.log_scan_scan_progress.setValue(100)
                            print("Count Max Done")
                            break
                    m = self.mlog.recv_match(type=match_types)

                    if m is None:
                        print("Mlog Loading Failed")
                        self.log_scan_scan_progress.setValue(0)
                        self.load_log.setEnabled(True)
                        break

                    available_types.add(m.get_type())
                    
                    # Grab the timestamp.
                    timestamp = getattr(m, '_timestamp', 0.0)
                    type = m.get_type()
                    data = m.to_dict()
                    data["timestamp"] = timestamp
                    if type == "ARM":
                        arm_state = data['ArmState']
                    if type == "RCOU":
                        rcou = data['C1']

                    if arm_state == 1 and rcou > 1000:
                        new_row = {}
                        if(type == "ESC"):
                            instance = data['Instance'] + 1
                            for key in data:
                                if key == 'RPM' or key == 'RawRPM'or  key == 'Volt'or  key == 'Curr'or  key == 'Temp'or  key == 'CTot'or  key == 'MotTemp'or  key == 'Err':
                                    new_row[key +"_"+str(instance)] = data[key]
                                else:
                                    new_row[key] = data[key]
                        else:
                            new_row = data
                        self.processed_df.loc[len(self.processed_df)] = new_row

                self.log_scan_scan_progress.setValue(90)
                self.processed_df.to_csv(filename+".csv", index=False)
                self.log_scan_scan_progress.setValue(100)
                print("Done")

            elif iscsv:
                self.log_scan_scan_progress.setValue(50)               

                self.processed_df = pd.read_csv(filename)
                if(self.processed_df.columns.values.tolist() == fields):
                    print("File Open")
                else:
                    print("File columns : " ,self.processed_df.columns.values.tolist())
                    print("Pre set columns : " , fields)
                    print("CSV Format incorrect")
                    self.log_scan_scan_progress.setValue(0)
                    self.load_log.setEnabled(True)
                    return "CSV Format incorrect"
                self.log_scan_scan_progress.setValue(100)

            else:
                print("File Format incorrect")
                self.log_scan_scan_progress.setValue(0)
                self.load_log.setEnabled(True)
                return "File Format incorrect"
        else:
            print("File Loading Failed")
            self.log_scan_scan_progress.setValue(0)
            self.load_log.setEnabled(True)
            return "Path not found"

        title = "ESC 1"
              
        # create plot window object
        plt = pg.plot()        
        plt.showGrid(x = True, y = True)
        plt.addLegend()        
        plt.setLabel('left', 'Vertical Values', units ='val')        
        plt.setLabel('bottom', 'Horizontal Values', units ='ms')            
        plt.setWindowTitle(title)
        plt.plotItem.setMouseEnabled()
        plt.setYRange(0, 7000)
        x =  self.processed_df["timestamp"].values.tolist()
        rcout =  self.processed_df["C1"].values.tolist()
        rpm =  self.processed_df["RPM_1"].values.tolist()
        volt =  self.processed_df["Volt_1"].values.tolist()
        curr =  self.processed_df["Curr_1"].values.tolist()
        temp =  self.processed_df["Temp_1"].values.tolist()
        
        line1 = plt.plot(x, rcout, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='Thr')
        line2 = plt.plot(x, rpm, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='rpm')
        line3 = plt.plot(x, volt,pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='volt')
        line4 = plt.plot(x, curr, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='curr')
        line5 = plt.plot(x, temp, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='temp')        
        
        title = "ESC 2"
              
        # create plot window object
        plt1 = pg.plot()        
        plt1.showGrid(x = True, y = True)
        plt1.addLegend()        
        plt1.setLabel('left', 'Vertical Values', units ='val')        
        plt1.setLabel('bottom', 'Horizontal Values', units ='ms')            
        plt1.setWindowTitle(title)
        plt1.plotItem.setMouseEnabled()
        plt1.setYRange(0, 7000)
        x =  self.processed_df["timestamp"].values.tolist()
        rcout =  self.processed_df["C2"].values.tolist()
        rpm =  self.processed_df["RPM_2"].values.tolist()
        volt =  self.processed_df["Volt_2"].values.tolist()
        curr =  self.processed_df["Curr_2"].values.tolist()
        temp =  self.processed_df["Temp_2"].values.tolist()
        
        line1 = plt1.plot(x, rcout, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='Thr')
        line2 = plt1.plot(x, rpm, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='rpm')
        line3 = plt1.plot(x, volt,pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='volt')
        line4 = plt1.plot(x, curr, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='curr')
        line5 = plt1.plot(x, temp, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='temp')        
        
        title = "ESC 3"
              
        # create plot window object
        plt3 = pg.plot()        
        plt3.showGrid(x = True, y = True)
        plt3.addLegend()        
        plt3.setLabel('left', 'Vertical Values', units ='val')        
        plt3.setLabel('bottom', 'Horizontal Values', units ='ms')            
        plt3.setWindowTitle(title)
        plt3.plotItem.setMouseEnabled()
        plt3.setYRange(0, 7000)
        x =  self.processed_df["timestamp"].values.tolist()
        rcout =  self.processed_df["C3"].values.tolist()
        rpm =  self.processed_df["RPM_3"].values.tolist()
        volt =  self.processed_df["Volt_3"].values.tolist()
        curr =  self.processed_df["Curr_3"].values.tolist()
        temp =  self.processed_df["Temp_3"].values.tolist()
        
        line1 = plt3.plot(x, rcout, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='Thr')
        line2 = plt3.plot(x, rpm, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='rpm')
        line3 = plt3.plot(x, volt,pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='volt')
        line4 = plt3.plot(x, curr, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='curr')
        line5 = plt3.plot(x, temp, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='temp')        

        title = "ESC 4"
              
        # create plot window object
        plt4 = pg.plot()        
        plt4.showGrid(x = True, y = True)
        plt4.addLegend()        
        plt4.setLabel('left', 'Vertical Values', units ='val')        
        plt4.setLabel('bottom', 'Horizontal Values', units ='ms')            
        plt4.setWindowTitle(title)
        plt4.plotItem.setMouseEnabled()
        plt4.setYRange(0, 7000)
        x =  self.processed_df["timestamp"].values.tolist()
        rcout =  self.processed_df["C4"].values.tolist()
        rpm =  self.processed_df["RPM_4"].values.tolist()
        volt =  self.processed_df["Volt_4"].values.tolist()
        curr =  self.processed_df["Curr_4"].values.tolist()
        temp =  self.processed_df["Temp_4"].values.tolist()
        
        line1 = plt4.plot(x, rcout, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='Thr')
        line2 = plt4.plot(x, rpm, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='rpm')
        line3 = plt4.plot(x, volt,pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='volt')
        line4 = plt4.plot(x, curr, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='curr')
        line5 = plt4.plot(x, temp, pen ='g', symbol ='x', symbolPen ='g',
                          symbolBrush = 0.2, name ='temp')        
     
    #File open dialouge
    def open(self):
        try: 
            fileName = QFileDialog.getOpenFileName(self)
            self.log_file_path.setText(fileName[0])
            print(fileName)
        except Exception as ex:
            print('Exception.', ex, self)
    
    def connect_can(self):
        try:
            # Initializing a DroneCAN node instance.
            self._node = dronecan.make_node( self.serial_com_box.currentText(), node_id=self.cpn_dev_id.value(), bitrate=args.bitrate)
            # Initializing a node monitor
            node_monitor = dronecan.app.node_monitor.NodeMonitor(self._node)

             # # Initializing a node monitor
            # callback for printing gps status 
            self._node_spin_timer.start(10)
            print("CAN Node Init Successful")

            self._subscriber_handle = self._node.add_handler(dronecan.uavcan.equipment.esc.Status, self.fetch_data)
            # setup to publish ESC RawCommand at 20Hz
            self._node.periodic(0.04, self.publish_throttle_setpoint)
            self._node.periodic(1, self.publish_arm_state)
            self.scan_group.setEnabled(True)
            self.thr_out_list = self.processed_df["C"+self.motor_selection.text()].values.tolist()
            self.thr_out_list = [x for x in self.thr_out_list if str(x) != 'nan']
            zero_list = list(0 for I in range (200))
            self.thr_out_list = zero_list + self.thr_out_list + zero_list

            self.run_time.setValue(int(len(self.thr_out_list)/25))
            print("CAN Node Processed")
        except Exception as e:
            print(e)
            # sys.exit()
       

    def publish_arm_state(self):
        if self.arm_requested == True:
            #publish safety Off
            message = dronecan.ardupilot.indication.SafetyState()
            message.status = message.STATUS_SAFETY_OFF
            self._node.broadcast(message)

            #publish ARM State
            message = dronecan.uavcan.equipment.safety.ArmingStatus()
            message.status = message.STATUS_FULLY_ARMED
            self._node.broadcast(message)

        else:
            #publish safety Off
            message = dronecan.ardupilot.indication.SafetyState()
            message.status = message.STATUS_SAFETY_ON
            self._node.broadcast(message)

            #publish ARM State
            message = dronecan.uavcan.equipment.safety.ArmingStatus()
            message.status = message.STATUS_DISARMED
            self._node.broadcast(message)

    def publish_throttle_setpoint(self):
        if self.arm_requested == True:
            #set Value of ESC raw
            setpoint = 0
            if self.thr_out_list_pt < len(self.thr_out_list):
                setpoint = self._convert_thr(int(self.thr_out_list[self.thr_out_list_pt]), 1000, 2000)
                self.thr_out_list_pt = self.thr_out_list_pt + 1

            self.thr_out_ls.append(str((setpoint/8191) *100))
            time = QDateTime.currentDateTime()
            time_display = time.toString('yyyy-MM-dd hh:mm:ss dddd')
            self.ts.append(time_display)

            self.thr_out_fig.add_data(int((setpoint/8191) *100)) 
            self._thr_value_out.setText(str(setpoint))
            commands = [setpoint, setpoint, setpoint, setpoint]
            message = dronecan.uavcan.equipment.esc.RawCommand(cmd=commands)
            self._node.broadcast(message)
            # print(setpoint)
        else:
            self.thr_out_list_pt = 0
            #set Value of ESC raw 0 
            setpoint = 0
            self._thr_value_out.setText(str(setpoint))
            commands = [setpoint, setpoint, setpoint, setpoint]
            message = dronecan.uavcan.equipment.esc.RawCommand(cmd=commands)
            self._node.broadcast(message)
       
    def fetch_data(self,msg):
        payload = msg.transfer.payload
        #check ESC telem
        if "uavcan.equipment.esc.Status" in str(payload):
            self._node_id.setText(msg.transfer.source_node_id)
            instance = int(msg.transfer.payload.esc_index) + 1
            if(self.motor_selection.text() == str(instance)):
                self.telem_rpm_ls.append(msg.transfer.payload.rpm)
                self.telem_volt_ls.append(msg.transfer.payload.voltage)
                self.telem_curr_ls.append(msg.transfer.payload.current)
                self.telem_temp_ls.append(str(msg.transfer.payload.temperature -273.15))
                self.telem_error_ls.append(msg.transfer.payload.error_count)
                time = QDateTime.currentDateTime()
                time_display = time.toString('yyyy-MM-dd hh:mm:ss dddd')
                self.ts.append(time_display)

                if len(self.telem_rpm_ls) > 0 : 
                    self.rpm_fig.add_data(self.telem_rpm_ls[-1]) 
                    self._tele_rpm.setText(str(self.telem_rpm_ls[-1]))

                if len(self.telem_volt_ls) > 0 : 
                    self.volt_fig.add_data(self.telem_volt_ls[-1]) 
                    self._tele_volt.setText(str(self.telem_volt_ls[-1]))
                if len(self.telem_curr_ls) > 0 : 
                    self.curr_fig.add_data(self.telem_curr_ls[-1]) 
                    self._tele_curr.setText(str(self.telem_curr_ls[-1]))
                if len(self.telem_temp_ls) > 0 : 
                    self.temp_fig.add_data(self.telem_temp_ls[-1]) 
                    self._tele_temp.setText(str(self.telem_temp_ls[-1]))

                if len(self.telem_error_ls) > 0 : 
                    self._tele_status.setText(str(self.telem_error_ls[-1]))
                

                if len(self.telem_temp_ls) > 0 :
                    if self.telem_temp_ls[-1] != None:
                        if self.telem_temp_ls[-1] > 85:
                            self._tele_temp.setStyleSheet("background-color: red; border: 1px solid black;")
                        else:
                            self._tele_temp.setStyleSheet("background-color: Green; border: 1px solid black;")
                if len(self.telem_error_ls) > 0 :           
                    if self.telem_error_ls[-1] != None:
                        if self.telem_error_ls[-1] != 0:
                            self._tele_status.setStyleSheet("background-color: red; border: 1px solid black;")
                        else:
                            self._tele_status.setStyleSheet("background-color: Green; border: 1px solid black;")

    def on_user_detail_changed(self):
        if self.user_name.text() != "" and self.user_email.text() != "":
            self.config_group.setEnabled(True)
            self.scan_value_group.setEnabled(True)

    def _convert_thr(self, thr, min, max):
        perct = ((thr - 1000)/1000 )* 100
        out = int(8191 * (perct/100))
        if out < 0 : out = 0
        if out > 8191 : out = 8191
        return out


    def show_time(self):
        time = QDateTime.currentDateTime()
        time_display = time.toString('yyyy-MM-dd hh:mm:ss dddd')
        self.current_timer_label.setText(time_display)
        
        time_elapsed = ((time.currentMSecsSinceEpoch() - self.start_time) /1000)
        self.time_elapsed_label.setText(str("%.1f sec"% time_elapsed))
        
        if time_elapsed > self.run_time.value() or self.thr_out_list_pt >= len(self.thr_out_list):
            self.disarm_btn.click()

        self.scan_progress.setValue(int(time_elapsed/(self.run_time.value()))* 100)

    def arm_timer(self):
        print("ARMED")
        self.arm_btn.setEnabled(False)
        self.disarm_btn.setEnabled(True)
        time = QDateTime.currentDateTime()
        time_display = time.toString('yyyy-MM-dd hh:mm:ss dddd')
        self.arm_timer_label.setText(time_display)
        self.start_time = time.currentMSecsSinceEpoch()

        self.timer.start(1000)
        #publish safety Off
        message = dronecan.ardupilot.indication.SafetyState()
        message.status = message.STATUS_SAFETY_OFF
        self._node.broadcast(message)

        #publish ARM State
        message = dronecan.uavcan.equipment.safety.ArmingStatus()
        message.status = message.STATUS_FULLY_ARMED
        self._node.broadcast(message)
        self.arm_requested = True




    def disarm_timer(self):
        print("DISARMED")
        self.timer.stop()
        self.arm_requested = False

        self.end_time = QDateTime.currentDateTime()
        time_display = self.end_time.toString('yyyy-MM-dd hh:mm:ss dddd')
        self.disarm_timer_label.setText(time_display)
        self.scan_progress.setValue(100)
        self.file_save()
        self.ts = []
        self.telem_rpm_ls = []
        self.telem_volt_ls = []
        self.telem_curr_ls = []
        self.telem_temp_ls = []
        self.telem_error_ls = []
        self.thr_out_ls = []
        self.thr_out_list_pt = 0
        time = QDateTime.currentDateTime()
        time_display = time.toString('yyyy-MM-dd hh:mm:ss dddd')
        self.telem_log_file_name = "esc_log_analysis_master"+time_display+".csv"

        # self.win_result.exec_()

        #handle end
        if self._subscriber_handle is not None:
            self._subscriber_handle.remove()
            self._subscriber_handle = None
        
        self.arm_btn.setEnabled(True)
        self.disarm_btn.setEnabled(False)

    def file_save(self):
        data_raw = [self.current_timer_label.text(), self.user_name.text(), self.user_email.text(), self.motor_details.text(), self.prop_details.text(),
                    self.esc_details.text(), self.cpn_dev_id.text(),self.log_file_path.text(),self.motor_selection.text(),self.ramp_prct_mod.text(),self.run_time.text(),self.start_time,self.end_time,"Pass",self.telem_log_file_name]
        data_file = pd.DataFrame([data_raw], columns=self.col_names)        
        data_file.to_csv(self.master_file_name, mode='a', index=False, header= False)

        # data_raw = [self.ts, self.thr_out_ls, self.telem_rpm_ls, self.telem_volt_ls, self.telem_curr_ls,self.telem_error_ls, self.telem_temp_ls]
        data_file = pd.DataFrame(columns=self.telem_col_names)   
        if len(self.ts)> 0 : data_file['Time Stamp'] = pd.Series(self.ts)
        if len(self.thr_out_ls)> 0 :data_file['Throttle Out'] = pd.Series(self.thr_out_ls)
        if len(self.telem_rpm_ls)> 0 :data_file['RPM'] = pd.Series(self.telem_rpm_ls)
        if len(self.telem_volt_ls)> 0 :data_file['Voltage'] = pd.Series(self.telem_volt_ls)
        if len(self.telem_curr_ls)> 0 :data_file['Current'] = pd.Series(self.telem_curr_ls)
        if len(self.telem_error_ls)> 0 :data_file['Error'] = pd.Series(self.telem_error_ls)
        if len(self.telem_temp_ls)> 0 :data_file['Temperature'] = pd.Series(self.telem_temp_ls)

        data_file.to_csv(self.telem_log_file_name, mode='a', index=False)

        print("file save")

    def _spin_node(self):
        # We're running the node in the GUI thread.
        # This is not great, but at the moment seems like other options are even worse.
        try:
            self._node.spin(0)
        except Exception as ex:
            msg = 'Node spin error : %r' % ( ex)
            self._node_spin_timer.stop()
            self._node.close()
    
    def __del__(self):
        global _singleton
        _singleton = None

    def closeEvent(self, event):
        global _singleton
        if self._subscriber_handle is not None:
            self._subscriber_handle.remove()
        _singleton = None
        super(ESCLogAnalysis, self).closeEvent(event)


def spawn(parent, node):
    global _singleton
    if _singleton is None:
        _singleton = ESCLogAnalysis(parent, node)

    _singleton.show()
    _singleton.raise_()
    _singleton.activateWindow()

    return _singleton


# get_icon = partial(get_icon, 'asterisk')

if __name__ == "__main__":
    parser = ArgumentParser(description='Fix2 gap example')
    parser.add_argument("--bitrate", default=1000000, type=int, help="CAN bit rate")
    parser.add_argument("--node-id", default=11, type=int, help="CAN node ID")
    parser.add_argument("--max_data_size", default=None, type=int, help="add the .log file path")
    parser.add_argument("--port", default=None, type=str, help="serial port or mavcan URI")
    args = parser.parse_args()

    node = 0
    
    app = QApplication(sys.argv)
    window = ESCLogAnalysis(node)
    app.exec_()