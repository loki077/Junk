import pandas as pd
import argparse
import matplotlib.pyplot as plt
import os
from matplotlib.widgets import CheckButtons
import numpy as np
from pymavlink import mavutil

def convert_tlog_to_csv(file:str , output_file_name:str='output.csv') -> None:
    # Open the TLOG files
    mlog = mavutil.mavlink_connection(file)
    print('Opened TLOG file: ' + file)
    # Iterate over the messages and store them in a list
    messages = []
    while True:
        msg = mlog.recv_msg()
        if msg is None:
            break
        if msg is not None:
            messages.append(msg.to_dict())
    # Convert the list to a DataFrame
    df = pd.DataFrame(messages)
    #save file
    df.to_csv(output_file_name, index=False)
    print('Saved CSV file: ' + output_file_name)

def convert_loop_sequence(series: pd.Series )-> pd.Series:
    offset = 0
    last_value = -1
    new_series = []

    for value in series:
        if value < last_value:
            offset += 256
        new_series.append(value + offset)
        last_value = value

    return new_series

def process_file(file_path: str) -> pd.DataFrame:
    print('Processing file: ' + file_path)
    df = pd.read_csv(file_path, header=None, engine='python', quoting=3, on_bad_lines='skip')
    df = df[~((df[6] == 'FF') & (df[7] == 'BE'))]
    df = df.dropna(subset=[0])
    df.loc[:, 0] = pd.to_datetime(df.loc[:, 0])
    df.loc[:, 0] = df.loc[:, 0].apply(lambda x: int(x.timestamp() * 1000))
    # Convert column 6 from hex to decimal
    df.loc[:, 5] = df.loc[:, 5].apply(lambda x: int(x, 16))
    df.loc[:, 5] = convert_loop_sequence(df.loc[:, 5])
    df = df[[0, 5, 8]]
    df.columns = ['timestamp', 'sequence', 'msg_type']
    df['sequence_diff'] = df['sequence'].diff().fillna(0)
    df['timestamp_diff'] = df['timestamp'].diff().fillna(0)
    print('Finished processing file: ' + file_path)
    return df


def plot_main_graph(df_4g:pd.DataFrame , df_rf:pd.DataFrame )-> None:
    print('Plotting main graph')
    def func(label: str )-> None:
        lines[label].set_visible(not lines[label].get_visible())
        plt.draw()
    # Create a new figure
    fig, ax = plt.subplots()

    # Enable navigation toolbar and grid
    plt.rcParams['toolbar'] = 'toolmanager'
    plt.rcParams['axes.grid'] = True

    # Convert Unix timestamp back to datetime
    df_rf['timestamp'] = pd.to_datetime(df_rf['timestamp'], unit='ms')
    df_4g['timestamp'] = pd.to_datetime(df_4g['timestamp'], unit='ms')

    # Plot sequence_diff against timestamp
    lines = {
        'rf_seq_diff': ax.plot(df_rf['timestamp'], df_rf['sequence_diff'], label='rf_seq_diff', picker=True)[0],
        'rf_ts_diff': ax.plot(df_rf['timestamp'], df_rf['timestamp_diff'], label='rf_ts_diff', picker=True)[0],
        '4g_seq_diff': ax.plot(df_4g['timestamp'], df_4g['sequence_diff'], label='4g_seq_diff', picker=True)[0],
        '4g_ts_diff': ax.plot(df_4g['timestamp'], df_4g['timestamp_diff'], label='4g_ts_diff', picker=True)[0]
        # '4g_rf_ts_diff': ax.plot(df_rf['timestamp'], df_rf['exists_in_df_4g'], label='4g_rf_ts_diff', picker=True)[0]
    }

    # Make a check button with all plotted lines with their labels
    rax = plt.axes([0, 0, 0.1, 0.1])
    labels = list(lines.keys())
    visibility = [line.get_visible() for line in lines.values()]
    check = CheckButtons(rax, labels, visibility)
    check.on_clicked(func)
    # Enable navigation toolbar
    plt.rcParams['toolbar'] = 'toolmanager'
    plt.rcParams['axes.grid'] = True


def plot_hist_graph(df:pd.DataFrame, title:str )-> None:
    print('Plotting histogram')
    # Create a new figure for the histogram
    plt.figure()
    # Define the bin edges
    bins = [0, 100, 250, 500, 1000, 5000, 15000, 30000, np.inf]

    # Drop NaN values from df_4g['timestamp_diff']
    df = df.dropna(subset=['timestamp_diff'])
    # Remove all rows where 'timestamp_diff' is 0
    df = df[df['timestamp_diff'] != 0]

    # Create a histogram of df['timestamp_diff'] with the defined bins, cumulative=True, and density=True
    n, bins, patches = plt.hist(df['timestamp_diff'], bins=bins, cumulative=True, density=True, histtype='step', color='blue', weights=df['timestamp_diff'])

    # Convert the histogram values to percentages
    n = n / n[-1] * 100

    # Display the histogram values on the graph
    for i in range(len(n)):
        if np.isfinite(bins[i]) and np.isfinite(n[i]):
            plt.text(bins[i], n[i], str(round(n[i], 2)))

    # Set the title and labels
    plt.title(f'CDF of timestamp_diff {title}')
    plt.xlabel('timestamp_diff')
    plt.ylabel('Cumulative probability')

    

def check_file_extension(file_path):
    if file_path == None:
        return None
    _, extension = os.path.splitext(file_path)
    if extension == '.csv':
        return 'csv'
    elif extension == '.tlog':
        return 'tlog'
    else:
        return 'none'

def main() -> None:
    if check_file_extension(args.path_4g) == 'tlog':
        convert_tlog_to_csv(args.path_4g, "4g_tlog.csv")
        convert_tlog_to_csv(args.path_4g, "rf_tlog.csv")
        path_4g = "4g_tlog.csv"
        path_rf = "rf_tlog.csv"
    elif check_file_extension(args.path_4g) == None:
        #check if file doest not exists 
        if not os.path.isfile("4g.csv") and not os.path.isfile("rf.csv"):
            print('csv File does not exists')
            return
        path_4g = "4g.csv"
        path_rf = "rf.csv"
    else:
        print('File extension not supported')
        return
    df_4g = process_file(path_4g)
    df_rf = process_file(path_rf)
    plot_main_graph(df_4g, df_rf)
    plot_hist_graph(df_4g, "4G") 
    plot_hist_graph(df_rf, "RF") 
    plt.show()
  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert TLOG to CSV.')
    parser.add_argument('--path_4g', type=str, help='Path to 4G TLOG file')
    parser.add_argument('--path_rf', type=str, help='Path to RF TLOG file')
    args = parser.parse_args()
    main()
