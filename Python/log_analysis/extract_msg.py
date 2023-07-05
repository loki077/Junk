import os
from pymavlink import mavutil

def extract_and_parse_logs(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.BIN'):
                log_path = os.path.join(root, file)
                print(f"Processing: {log_path}")

                # Open the log file
                log = mavutil.mavlink_connection(log_path)

                # Process the log messages
                while True:
                    msg = log.recv_match(type='MSG')
                    if msg is None:
                        break
                    if 'EKF3 lane switch' in msg.Message:
                        print(f'Timestamp: {msg.TimeUS} | Message: {msg.Message}')

logs_folder_path = 'D:\\Logs\\V34'
extract_and_parse_logs(logs_folder_path)

print("Script End")