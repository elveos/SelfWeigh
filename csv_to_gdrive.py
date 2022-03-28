#!/usr/bin/python3

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import multiprocessing as mp
from settings_main import csv_remote, csv_folder_id

def main():
	gauth = GoogleAuth()
	#gauth.LocalWebserverAuth()# Creates local webserver and auto handles authentication; uncomment during the first launch to authenticate Google Drive.
	drive = GoogleDrive(gauth)


	#upload image to the folder
	#file2 = drive.CreateFile({'title':'weighlist.csv',
	#						  'mimeType':'text/csv',
	#						  'parents': [{"kind": "drive#fileLink", "id": csv_folder_id}]
	#						  })


	file_list_var = ("{'q':"+"'"+csv_folder_id+"'"+" in parents and trashed=False"+'"}')
	file_list = drive.ListFile(file_list_var).GetList()

	for x in range(len(file_list)):
		if file_list[x]['title'] == 'weighlist':
			file_id = file_list[x]['id']

	file2 = drive.CreateFile({'id':file_id})
	file2.SetContentFile(csv_remote)##local file to upload
	file2.Upload({'convert': True})

if __name__ == "__main__":
	main()
