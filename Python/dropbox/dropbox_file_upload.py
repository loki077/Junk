import dropbox
from dropbox.exceptions import AuthError

# Path to the log file
log_file_path = "data.log"

# Dropbox access token
access_token = "sl.BfbHxfu95uCpKe-KHXD5wHu-pfegeyLKczmX1sv5G0IqRPszZ-g2V2hcXiMVD-Le5DN91L4COq6M7AZlQhIzjQuJs0QNC9b_xAs4ktGSqqG6vmoIjKWnL-YdFw0M3uYLBGqqoDDqQvA"

# Create a Dropbox client
try:
    dbx = dropbox.Dropbox(access_token)
except AuthError as e:
    print('Error connecting to Dropbox with access token: ' + str(e))


# Upload the file
try:
    with open(log_file_path, "rb") as file:
        dbx.files_upload(file.read(), "logfile.log")
    print("File uploaded successfully!")
except Exception as e:             
    print('Error uploading file to Dropbox: ' + str(e))
