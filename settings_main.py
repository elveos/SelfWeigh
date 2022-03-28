## Serial port settings ##
serial_port = "/dev/ttyV0"
serial_baud = 9600

"""
HikVision get photo example:
"http://user:password@192.168.1.64/ISAPI/Streaming/channels/102/picture"

Generic cam video stream URL example in case that grabbing direct JPG from camera isn't possible:
"rtsp://admin:@192.168.1.204:554/11"
"""


## JPG/stream URL for each camera. Reading order is 1-4. ##
# An actual URL may vary for each camera.
url_cam1 = 'rtsp://admin:@192.168.1.104:554/11'
url_cam2 = 'rtsp://admin:@192.168.1.105:554/11'
url_cam3 = 'rtsp://admin:@192.168.1.106:554/11'
url_cam4 = 'rtsp://admin:@192.168.1.107:554/11' 

## File locations (can be left at default values) ##
# csv_remote is main weighlist on main(server) pi
csv_remote = "~/SelfWeigh/weighlist.csv"
#csv_local = "~/SelfWeigh/weighlist_outdoor1.csv"
vars_local = "~/SelfWeigh/vars.py"
tracker_local = "~/SelfWeigh/tracker.txt"

## Plate Recognizer API ##
# Once you create an account on https://platerecognizer.com,
# paste your API token from https://app.platerecognizer.com/accounts/plan/ here:
pr_token=''

## Google Drive API ##
# Enter your Google API Client ID and Client Secret in settings.yaml
# Create two folders in your Google Drive root dir.
# Each folder's ID is the last part of URL when you open the folder.
csv_folder_id = ''
img_folder_id = ''

## Weigh slip addend ##
# Each weigh slip's ID equals to its row number in weighlist.csv.
# If weightlist was emptied, addend number can be set to keep the ID consistency.
wslip_addend = 0
