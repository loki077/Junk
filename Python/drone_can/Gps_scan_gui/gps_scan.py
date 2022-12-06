import dronecan
from functools import partial
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QDialog, QSlider, QSpinBox, QDoubleSpinBox, \
    QPlainTextEdit, QCheckBox, QGridLayout, QGroupBox , QApplication, QPushButton, QLineEdit, QProgressBar, QMessageBox
from PyQt5.QtCore import QTimer, Qt, QDateTime
from logging import getLogger
import pandas as pd
from pathlib import Path
import re


#can be excluded
import sys
from argparse import ArgumentParser


__all__ = 'PANEL_NAME', 'spawn', 'get_icon'

PANEL_NAME = 'GPS Scan Panel'


logger = getLogger(__name__)

_singleton = None

class GPSScanDataType:

    def __init__(self, pass_perct):
        self.total_cnt = 0
        self.total_fail = 0
        self.max = 0
        self.min = None
        self.avg = 0
        self.pass_perct = pass_perct
        self.start_rec = False

    def feed_val(self, value):
        if self.start_rec:
            self.total_cnt +=1
            self.check_max_min(value)
    
    def feed_err(self, value):
        if self.start_rec:
            self.total_cnt +=1
            self.total_fail +=1
            self.check_max_min(value)

    def check_max_min(self,value):
        if self.start_rec:
            if(value > self.max):
                self.max = value
            if self.min != None:
                if(value < self.min):
                    self.min = value
            else:
                self.min = value

    def get_result(self):
        per = ((self.total_cnt - self.total_fail)/self.total_cnt) *100
        return True if (per >= self.pass_perct) else False

    def get_result_str(self):
        per = ((self.total_cnt - self.total_fail)/self.total_cnt) *100
        return "Performance : %s Total Data : %d Total Fail : %d Max Value : %s Min Value : %s \n" %(str(per), self.total_cnt, self.total_fail, str(self.max), str(self.min) )

class GPSScanResult(QMessageBox):
    def __init__(self, ):
        super(GPSScanResult, self).__init__()
        self.setWindowTitle('GPS Scan Result \t\t\t\t\t\t\t\t\t\t\t')
    
    def fail_result(self, msg):
        self.setText("Test FAILED!")
        self.setDetailedText(msg)
        self.setIcon(QMessageBox.Critical)

    def success_result(self, msg):
        self.setText("Test SUCCESSFUL!")
        self.setDetailedText(msg)
        self.setIcon(QMessageBox.Information)

class GPSScan(QDialog):
    DEFAULT_INTERVAL = 0.1

    CMD_BIT_LENGTH = dronecan.get_dronecan_data_type(dronecan.uavcan.equipment.esc.RawCommand().cmd).value_type.bitlen
    CMD_MAX = 2 ** (CMD_BIT_LENGTH - 1) - 1
    CMD_MIN = -(2 ** (CMD_BIT_LENGTH - 1))

    def __init__(self, node):
        super(GPSScan, self).__init__()
        self.setWindowTitle('GPS Scan')
        self.setAttribute(Qt.WA_DeleteOnClose)              # This is required to stop background timers!

        self.data_key = {"last_fix_time_ms":0,"last_message_time_ms":0,"delta_time_ms":0,"delayed_count":0,"average_delta_ms":0, "lagged_sample_count":0}

        #create File
        self.col_names = ['Time Stamp',
             'Username',
             'Email',
             'GPS Device ID',
             'CPN Dev ID',
             'Test Start TS',
             'Test End TS',
             'Final Status',
             'Satellite Status',
             'Satellite Total Count',
             'Satellite Fail Count',
             'Satellite Max',
             'Satellite Min',
             'HDOP Status',
             'HDOP Total Count',
             'HDOP Fail Count',
             'HDOP Max',
             'HDOP Min',
             'Loop delay Status',
             'Loop delay Total Count',
             'Loop delay Fail Count',
             'Loop delay Max',
             'Loop delay Min',
             'ARM Status',
             'ARM Total Count',
             'ARM Fail Count',
             'ARM Max',
             'ARM Min',
             'Lat', 
             'Long']

        self.master_file_name = "gps_scan_master.csv"
        self.master_file_path = Path(self.master_file_name)

        if self.master_file_path.exists():
            self.master_file = pd.read_csv(self.master_file_path)
            print("File Open")
        else:
            self.master_file = pd.DataFrame([], columns=self.col_names)
            self.master_file.to_csv(self.master_file_name)
            print("File Created")

        #result widget
        self.win_result = GPSScanResult()

        #drone can parameter
        self._node = node        
        self._subscriber_handle = None

        #timmer parameter
        self.start_time = None
        self.end_time = None

        #gps scan parameter
        self.last_fix2 = {}
        self.sat_var = GPSScanDataType(99)
        self.hdop_var = GPSScanDataType(99)
        self.loop_delay_var = GPSScanDataType(99)
        self.arm_status_var = GPSScanDataType(99)

        #layout
        layout = QVBoxLayout(self)
        
        self._node_spin_timer = QTimer(self)
        self._node_spin_timer.timeout.connect(self._spin_node)
        self._node_spin_timer.setSingleShot(False)
        self._node_spin_timer.start(10)

        #Operator Details
        self.user_name = QLineEdit(self)
        self.user_email = QLineEdit(self)
        self.gps_dev_id = QLineEdit(self)
        self.cpn_dev_id = QLineEdit(self)

        self.user_detail_group = QGroupBox('User Details', self)
        user_detail_layout = QGridLayout(self)
        user_detail_layout.addWidget(QLabel('User Name  :', self),   0,0)
        user_detail_layout.addWidget(self.user_name,                 0,1)
        user_detail_layout.addWidget(QLabel('User Email :', self),   1,0)
        user_detail_layout.addWidget(self.user_email,                1,1)
        user_detail_layout.addWidget(QLabel('GPS Dev ID :', self),   2,0)
        user_detail_layout.addWidget(self.gps_dev_id,                2,1)
        user_detail_layout.addWidget(QLabel('CPN Dev ID :', self),   3,0)
        user_detail_layout.addWidget(self.cpn_dev_id,                3,1)
        self.user_detail_group.setLayout(user_detail_layout)

        # Config Value param  

        self.node_id = QSpinBox(self)
        self.node_id.setMaximum(10000)
        self.node_id.setMinimum(1)
        self.node_id.setValue(225)

        self.sat_thr = QSpinBox(self)
        self.sat_thr.setMaximum(50)
        self.sat_thr.setMinimum(0)
        self.sat_thr.setValue(12)

        self.hdop_thr = QLineEdit(self)
        self.hdop_thr.setText("1.5")       

        self.loop_thr = QSpinBox(self)
        self.loop_thr.setMaximum(10000)
        self.loop_thr.setMinimum(0)
        self.loop_thr.setValue(220)

        self.scan_time = QSpinBox(self)
        self.scan_time.setMaximum(10000)
        self.scan_time.setMinimum(1)
        self.scan_time.setValue(5)

        self.connect_btn = QPushButton('Connect')
        self.connect_btn.clicked.connect(self.connect_can)

        self.config_group = QGroupBox('Configure Parameter', self)
        config_layout = QGridLayout(self)
        config_layout.addWidget(QLabel('Node ID        :', self),   0,0)
        config_layout.addWidget(self.node_id,                       0,1)
        config_layout.addWidget(QLabel('Satellite Thr  <', self),   1,0)
        config_layout.addWidget(self.sat_thr,                       1,1)
        config_layout.addWidget(QLabel('HDOP Thr       >', self),   2,0)
        config_layout.addWidget(self.hdop_thr,                      2,1)
        config_layout.addWidget(QLabel('Loop Delay Thr >', self),   3,0)
        config_layout.addWidget(self.loop_thr,                      3,1)
        config_layout.addWidget(QLabel('Total Scan time:', self),   4,0)
        config_layout.addWidget(self.scan_time,                     4,1)
        config_layout.addWidget(self.connect_btn,                   5,0,1,2)
        self.config_group.setLayout(config_layout)
        self.config_group.setEnabled(False)

        # Live value param
        self._node_id_display   = QLabel('0', self)
        self._sat_count_display = QLabel('0', self)
        self._hdop_val_display  = QLabel('0', self)
        self._lat_display       = QLabel('0', self)
        self._long_display      = QLabel('0', self)
        self._loop_delay_display = QLabel('0', self)
        self._arm_status_display = QLabel('0', self)


        self.scan_value_group = QGroupBox('Live Value', self)
        scan_value_layout = QGridLayout(self)
        scan_value_layout.addWidget(QLabel('Node Id:', self),     0,0)
        scan_value_layout.addWidget(self._node_id_display,        0,1)
        scan_value_layout.addWidget(QLabel('Sat Count :', self),  1,0)
        scan_value_layout.addWidget(self._sat_count_display,      1,1)
        scan_value_layout.addWidget(QLabel('HDOP value:', self),  2,0)
        scan_value_layout.addWidget(self._hdop_val_display,       2,1)
        scan_value_layout.addWidget(QLabel('Latitude:', self),    3,0)
        scan_value_layout.addWidget(self._lat_display,            3,1)
        scan_value_layout.addWidget(QLabel('Longitude', self),    4,0)
        scan_value_layout.addWidget(self._long_display,           4,1)
        scan_value_layout.addWidget(QLabel('Loop Delay', self),   5,0)
        scan_value_layout.addWidget(self._loop_delay_display,     5,1)
        scan_value_layout.addWidget(QLabel('ARM Status', self),   6,0)
        scan_value_layout.addWidget(self._arm_status_display,     6,1)
        self.scan_value_group.setLayout(scan_value_layout)
        self.scan_value_group.setEnabled(False)

        #start scan
        self.start_timer_label=QLabel('Start time')
        self.end_timer_label=QLabel('End Time')
        self.current_timer_label=QLabel('Time')
        self.time_elapsed_label=QLabel('0')
        self.start_btn = QPushButton('Start Scan')
        self.end_btn   = QPushButton('End Scan')
        self.generate_report_button = QPushButton('Generate Report')

        self.timer = QTimer()
        self.timer.timeout.connect(self.show_time)
        self.start_btn.clicked.connect(self.start_timer)
        self.end_btn.clicked.connect(self.end_timer)
        self.generate_report_button.clicked.connect(self.file_save)
        self.scan_progress = QProgressBar(self)

        self.scan_group = QGroupBox('Test GPS', self)
        scan_layout = QGridLayout(self)
        scan_layout.addWidget(QLabel('Time', self),         0,0)
        scan_layout.addWidget(self.current_timer_label,     0,1)
        scan_layout.addWidget(QLabel('Start Time', self),   1,0)
        scan_layout.addWidget(self.start_timer_label,       1,1)
        scan_layout.addWidget(QLabel('Stop Time', self),    2,0)
        scan_layout.addWidget(self.end_timer_label,         2,1)
        scan_layout.addWidget(QLabel('Time elapsed', self), 3,0)
        scan_layout.addWidget(self.time_elapsed_label,      3,1)
        scan_layout.addWidget(self.start_btn,                4,0)
        scan_layout.addWidget(self.end_btn,                  4,1)
        scan_layout.addWidget(self.scan_progress,           5,0,1,2)
        # scan_layout.addWidget(self.generate_report_button,  6,0,1,2)
        self.scan_group.setLayout(scan_layout)
        self.scan_group.setEnabled(False)

        #Generate Report 

        #Final Value
        layout.addWidget(self.user_detail_group)
        layout.addWidget(self.config_group)
        layout.addWidget(self.scan_value_group)
        layout.addWidget(self.scan_group)

        self.setLayout(layout)
        self.resize(600 if (self.minimumWidth()< 300) else self.minimumWidth(), self.minimumHeight())

        #connect 
        self.user_name.textChanged.connect(self.on_user_detail_changed)
        self.user_email.textChanged.connect(self.on_user_detail_changed)
        self.gps_dev_id.textChanged.connect(self.on_user_detail_changed)
        self.cpn_dev_id.textChanged.connect(self.on_user_detail_changed)
        
    def connect_can(self):
        # callback for printing gps status 
        self._subscriber_handle = self._node.add_handler(dronecan.uavcan.equipment.gnss.Auxiliary, self.fetch_data)
        self._subscriber_handle = self._node.add_handler(dronecan.uavcan.equipment.gnss.Fix2, self.fetch_data)
        self._subscriber_handle = self._node.add_handler(dronecan.ardupilot.gnss.Status, self.fetch_data)
        self._subscriber_handle  = self._node.add_handler(dronecan.uavcan.protocol.debug.LogMessage, self.fetch_data)

        self.scan_group.setEnabled(True)

    def fetch_data(self,msg):
        payload = msg.transfer.payload

        #check Hdop value
        if "uavcan.equipment.gnss.Auxiliary" in str(payload):
            node_id = msg.transfer.source_node_id
            hdop = msg.transfer.payload.hdop

            self._node_id_display.setText(str(node_id))
            self._hdop_val_display.setText(str(hdop))

            if self.hdop_thr.text() != None:
                if hdop > float(self.hdop_thr.text()):
                    self._hdop_val_display.setStyleSheet("background-color: red; border: 1px solid black;")
                    self.hdop_var.feed_err(hdop)
                else:
                    self._hdop_val_display.setStyleSheet("background-color: Green; border: 1px solid black;")
                    self.hdop_var.feed_val(hdop)

        #check sat cnt, lat, long, loop delay
        if "uavcan.equipment.gnss.Fix2" in str(payload):
            sat_cnt  = msg.transfer.payload.sats_used
            lat = msg.transfer.payload.latitude_deg_1e8
            long = msg.transfer.payload.longitude_deg_1e8
            node_id = msg.transfer.source_node_id

            self._node_id_display.setText(str(node_id))
            self._sat_count_display.setText(str(sat_cnt))
            self._lat_display.setText(str(lat))
            self._long_display.setText(str(long))

            if sat_cnt < float(self.sat_thr.value()): 
                self._sat_count_display.setStyleSheet("background-color: red; border: 1px solid black;")
                self.sat_var.feed_err(sat_cnt)
            else:
                self._sat_count_display.setStyleSheet("background-color: Green; border: 1px solid black;")
                self.sat_var.feed_val(sat_cnt)

            if lat == 0: 
                self._lat_display.setStyleSheet("background-color: red; border: 1px solid black;")
            else:
                self._lat_display.setStyleSheet("background-color: Green; border: 1px solid black;")

            if long == 0: 
                self._long_display.setStyleSheet("background-color: red; border: 1px solid black;")
            else:
                self._long_display.setStyleSheet("background-color: Green; border: 1px solid black;")

            #calculate the loop interval of Fix2
            t_stamp = msg.transfer.ts_real
            if not node_id in self.last_fix2:
                self.last_fix2[node_id] = t_stamp
                return
            loop_delay = t_stamp - self.last_fix2[node_id]
            self.last_fix2[node_id] = t_stamp

            self._loop_delay_display.setText(str("%.3f ms"% loop_delay))
            if loop_delay > float(self.loop_thr.value()):
                self._loop_delay_display.setStyleSheet("background-color: red; border: 1px solid black;")
                self.loop_delay_var.feed_err(loop_delay)
            else:
                self._loop_delay_display.setStyleSheet("background-color: Green; border: 1px solid black;")
                self.loop_delay_var.feed_val(loop_delay)
        
        #check arming status
        if "ardupilot.gnss.Status" in str(payload):
            node_id = msg.transfer.source_node_id
            if "False" in str(payload):
                self._arm_status_display.setText("False")
                self._arm_status_display.setStyleSheet("background-color: red; border: 1px solid black;")
                self.arm_status_var.feed_err(0)
            else:
                self._arm_status_display.setText("True")
                self._arm_status_display.setStyleSheet("background-color: green; border: 1px solid black;")
                self.arm_status_var.feed_val(1)
        
        if "uavcan.protocol.debug.LogMessage" in str(payload):
            text = dronecan.to_yaml(payload)
            if "GPS_LOG" in text:
                result = re.search('\'GPS_LOG,(.+?) \' #', text)
                if result:
                    data = result.group(1).split(",")
                    i = 0
                    for key in self.data_key:
                        self.data_key[key] = data[i]
                        i+=1
                    print(self.data_key)



    def on_user_detail_changed(self):
        if self.user_name.text() != "" and self.user_email.text() != "" and self.gps_dev_id.text() != "" and self.cpn_dev_id.text() != "":
            self.config_group.setEnabled(True)
            self.scan_value_group.setEnabled(True)

    def show_time(self):
        time = QDateTime.currentDateTime()
        time_display = time.toString('yyyy-MM-dd hh:mm:ss dddd')
        self.current_timer_label.setText(time_display)
        
        time_elapsed = ((time.currentMSecsSinceEpoch() - self.start_time) /1000)/60
        self.time_elapsed_label.setText(str("%.1f min"% time_elapsed))
        if time_elapsed > int(self.scan_time.value()):
            self.end_btn.click()
        self.scan_progress.setValue((time_elapsed/int(self.scan_time.value()))* 100)

    def start_timer(self):
        time = QDateTime.currentDateTime()
        time_display = time.toString('yyyy-MM-dd hh:mm:ss dddd')
        self.start_timer_label.setText(time_display)
        self.start_time = time.currentMSecsSinceEpoch()

        self.sat_var.start_rec = self.hdop_var.start_rec = self.loop_delay_var.start_rec = self.arm_status_var.start_rec = True
        self.timer.start(1000)
        self.start_btn.setEnabled(False)
        self.end_btn.setEnabled(True)

    def end_timer(self):
        self.end_time = QDateTime.currentDateTime()
        time_display = self.end_time.toString('yyyy-MM-dd hh:mm:ss dddd')
        self.end_timer_label.setText(time_display)
        self.sat_var.start_rec = self.hdop_var.start_rec = self.loop_delay_var.start_rec = self.arm_status_var.start_rec = False
        self.scan_progress.setValue(100)

        #get result
        # try:
        out_str = "SATTELITE: \n " + self.sat_var.get_result_str() + "HDOP: \n " + self.hdop_var.get_result_str() + "Loop Delay: \n " + self.loop_delay_var.get_result_str() + "Arm Status: \n " + self.arm_status_var.get_result_str() 
        out_str = out_str + " Lat : %s Long : %s "%(self._lat_display.text(), self._long_display.text())
        if self.sat_var.get_result() and self.hdop_var.get_result() and self.loop_delay_var.get_result() and self.arm_status_var.get_result():
            self.win_result.success_result(out_str)
            self.file_save("Pass")
        else:
            self.win_result.fail_result(out_str)
            self.file_save("Fail")
        self.win_result.exec_()
        # except Exception as ex:
        #     print('Exception.', ex, self)
        
        #handle end
        if self._subscriber_handle is not None:
            self._subscriber_handle.remove()
            self._subscriber_handle = None
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.end_btn.setEnabled(False)

    def file_save(self, status):
        data_raw = [self.current_timer_label.text(), self.user_name.text(), self.user_email.text(), self.gps_dev_id.text(), self.cpn_dev_id.text(),
                    self.start_timer_label.text(), self.end_timer_label.text(), status,
                    self.sat_var.get_result(), self.sat_var.total_cnt, self.sat_var.total_fail, self.sat_var.max, self.sat_var.min,
                    self.hdop_var.get_result(), self.hdop_var.total_cnt, self.hdop_var.total_fail, self.hdop_var.max, self.hdop_var.min,
                    self.loop_delay_var.get_result(), self.loop_delay_var.total_cnt, self.loop_delay_var.total_fail, self.loop_delay_var.max, self.loop_delay_var.min,
                    self.arm_status_var.get_result(), self.arm_status_var.total_cnt, self.arm_status_var.total_fail, self.arm_status_var.max, self.arm_status_var.min,
                    self._lat_display.text(), self._long_display.text()]
        print(data_raw)
        data_file = pd.DataFrame([data_raw], columns=self.col_names)        
        data_file.to_csv(self.master_file_name, mode='a', index=False, header=False)

    def _spin_node(self):
        # We're running the node in the GUI thread.
        # This is not great, but at the moment seems like other options are even worse.
        try:
            self._node.spin(0)
            self._successive_node_errors = 0
        except Exception as ex:
            self._successive_node_errors += 1

            msg = 'Node spin error [%d of %d]: %r' % (self._successive_node_errors, self.MAX_SUCCESSIVE_NODE_ERRORS, ex)
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
        super(GPSScan, self).closeEvent(event)


def spawn(parent, node):
    global _singleton
    if _singleton is None:
        _singleton = GPSScan(parent, node)

    _singleton.show()
    _singleton.raise_()
    _singleton.activateWindow()

    return _singleton


# get_icon = partial(get_icon, 'asterisk')

if __name__ == "__main__":
    parser = ArgumentParser(description='Fix2 gap example')
    parser.add_argument("--bitrate", default=1000000, type=int, help="CAN bit rate")
    parser.add_argument("--node-id", default=11, type=int, help="CAN node ID")
    parser.add_argument("--max-gap", default=0.25, type=int, help="max gap in seconds")
    parser.add_argument("--min-sat", default=10, type=int, help="min sat count")
    parser.add_argument("--max-hdop", default=2.25, type=float, help="max hdop value")
    parser.add_argument("port", default=None, type=str, help="serial port or mavcan URI")
    args = parser.parse_args()

    try:
        # Initializing a DroneCAN node instance.
        node = dronecan.make_node(args.port, node_id=26, bitrate=args.bitrate)
        # Initializing a node monitor
        node_monitor = dronecan.app.node_monitor.NodeMonitor(node)
        print("CAN Node Init Successful")
    except Exception as e:
        print(e)
        sys.exit()
    app = QApplication(sys.argv)
    window = GPSScan(node)
    window.show()
    app.exec_()