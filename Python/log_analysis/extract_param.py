from pymavlink import mavutil

# Path to the bin log file
log_file = 'D:\\Logs\\V34\\20220912\\1.BIN'

# Parameter name to fetch
param_name = 'GPS_TYPE'

def fetch_parameter_from_binlog(binlog_file, parameter_name):
    # Open the bin log file
    mlog = mavutil.mavlink_connection(binlog_file)

    # Iterate over the messages in the bin log
    while True:
        msg = mlog.recv_match(type='PARAM_VALUE', blocking=True)
        if msg is None:
            print('End of file')
            break
        print('name: %s\tvalue: %d' %(msg['param_id'].decode("utf-8"), msg['param_value']))
        # Check if the parameter name matches
        # if msg.param_id == parameter_name:
        #     print(f"Parameter {parameter_name}: {msg.param_value}")
        #     # Print the parameter value
        #     return

# Call the function to fetch the parameter
fetch_parameter_from_binlog(log_file, param_name)
