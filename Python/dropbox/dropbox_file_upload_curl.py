import subprocess
import json

def upload_file_to_dropbox_curl(file_path, dropbox_path, access_token):
    """
    Upload a file to Dropbox using curl command.

    :param file_path: Path to the local file to be uploaded.
    :param dropbox_path: The path in Dropbox where the file will be stored.
    :param access_token: Your Dropbox API access token.
    """

    # Prepare the header and the data for the curl command
    headers = {
        "Authorization": "Bearer " + access_token,
        "Dropbox-API-Arg": json.dumps({"path": dropbox_path, "mode": "add", "autorename": True, "mute": False}),
        "Content-Type": "application/octet-stream"
    }

    header_string = " ".join(["-H \"{}: {}\"".format(k, v) for k, v in headers.items()])

    # Prepare the curl command
    curl_command = "curl -X POST https://content.dropboxapi.com/2/files/upload {} --data-binary @{}".format(header_string, file_path)

    # Execute the curl command
    subprocess.run(curl_command, shell=True)

# Example usage
file_path = "path/to/your/local/file"
dropbox_path = "/path/in/dropbox"
access_token = "your_access_token"
upload_file_to_dropbox_curl(file_path, dropbox_path, access_token)
