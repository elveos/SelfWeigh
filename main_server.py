#!/usr/bin/python3

import subprocess, time, csv, requests, json, serial
import cv2, re, sys, os, gc
import pandas as pd
import numpy as np
from tkinter import *
import tkinter as tk
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import multiprocessing as mp

from settings_main import *
from plates_categories import *

pathweighslip = os.path.abspath('weighslip.py')
pathweighslip_server = os.path.abspath('weighslip_server.py')
path_csv_to_gdrive = os.path.abspath('csv_to_gdrive.py')
pathlive = os.path.abspath('live.py')
rega, vag_rega, vaganje, neto, vag_neto, v1, v2, vlist, comvalue, ulaz, vag_prijevoznik = [None] * 11
ser = serial.Serial(serial_port, serial_baud)

font = cv2.FONT_HERSHEY_SIMPLEX
org = (1640,50)
org2 = (1640,80)
org3 = (1640,110)
org4 = (1640,140)
org5 = (1580,170)
fontScale = 1
color = (255,255,255)
thickness = 2

def main():
	def ungray():
		b1.config(state='normal')
	def grayout():
		b1.config(state='disabled')
		b1.after(7000, lambda:ungray())
	def ungray2():
		b2.config(state='normal')
	def grayout2():
		b2.config(state='disabled')
		b2.after(7000, lambda:ungray2())
		
	def upload_slike(lokacija_slike,ime_slike):
		gauth = GoogleAuth()
		#gauth.LocalWebserverAuth()# Creates local webserver and auto handles authentication: Uncomment to authenticate during first launch.
		drive = GoogleDrive(gauth)
		
		#upload image to the folder
		file2 = drive.CreateFile({'title':ime_slike,
								  'mimeType':'image/jpeg',
								  'parents': [{"kind": "drive#fileLink", "id": img_folder_id}]
								  })
		#In parents argument above we need to specify the folder ID of the folder to which it has to be uploaded.
		#mimeType is different for each file type, which are available in the google api documentation.

		#specify the local path with the quotes in the below line
		up_lokacija = lokacija_slike + ime_slike
		file2.SetContentFile(up_lokacija)
		file2.Upload()

		#SET PERMISSION
		permission = file2.InsertPermission({
									'type': 'anyone',
									'value': 'anyone',
									'role': 'reader'})

		#SHARABLE LINK
		link=file2['alternateLink']

		#To use the image in Gsheet we need to modify the link as follows
		link=file2['alternateLink']
		link=link.split('?')[0]
		link=link.split('/')[-2]
		link='https://docs.google.com/uc?export=download&id='+link
		return (link)
	

	def upload_csv():
		gauth = GoogleAuth()
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
	
	def readcom():
		global comvalue
		cc=str(ser.readline().decode())
		try:
			comvalue0=re.search('[0-9]{2,5}', cc).group()
		except:
			cc=str(ser.readline().decode())
			comvalue0=re.search('[0-9]{2,5}', cc).group()
			print('Potencijalna greska kod cc.group')

		time.sleep(1.5)

		cc2=str(ser.readline().decode())
		try:
			comvalue1=re.search('[0-9]{2,5}', cc2).group()
		except:
			cc=str(ser.readline().decode())
			comvalue1=re.search('[0-9]{2,5}', cc2).group()
			print('Potencijalna greska kod cc.group')
	
		comvalue0_int = int(comvalue0)
		comvalue1_int = int(comvalue1)
		if comvalue0_int == comvalue1_int:
			comvalue = comvalue0
			return comvalue
		else:
			readcom()


	def grab_image():
		global frame
		cap = cv2.VideoCapture(url_cam1)
		if cap.isOpened():
			_,frame = cap.read()
			cap.release()
			if _ and frame is not None:
				cv2.imwrite('last.jpg', frame)
				return frame


	def prepoznavanje_tablica():
		global rega
		def prepkod():
			global rega
			global vag_rega
			global frame
			rega = None
			# Get JPG from video stream
			if cap.isOpened():
				_,frame = cap.read()
				cap.release() #releasing camera immediately after capturing picture
				if _ and frame is not None:
					cv2.imwrite('last.jpg', frame)
					return frame
			# PlateRecognizer API
			regions = ['hr']
			headers_var = "{'Authorization'}:" + "'Token " + pr_token + "'}"
			with open('~/SelfWeigh/last.jpg', 'rb') as fp:
				response = requests.post(
					'https://api.platerecognizer.com/v1/plate-reader/',
					data=dict(regions=regions),  # Optional
					files=dict(upload=fp),
					headers=headers_var)
			os.system('rm last.jpg')
			data = response.json()
			ucitanje = json.dumps(data)
			# Search plate format and extract it from JSON
			ss = re.search('[a-z]{2,2}[0-9]{3,4}[a-z]{2,2}', ucitanje)
			s =  re.search('[a-z]{2,2}[0-9]{3,4}[a-z]{1,2}', ucitanje)
			if ss == None:
				prerega = s
			else:
				prerega = ss
			vag_rega = prerega.group()
			rega = prerega.group()
			
			print ("Recognized plate:", rega)
			# prioriteti kamera:
			# 1. ulaz: 1 2 4 3
			# 2. ulaz: 4 3 1 2
	
		try:
			rega = None
			cap = None
			if ulaz == 1:
				print ("Čitanje iz kamere 1...")
				cap = cv2.VideoCapture(url_cam1)			
			elif ulaz == 2:
				print ("Čitanje iz kamere 4...")
				cap = cv2.VideoCapture(url_cam4)
			prepkod()	
		except:
			try:
				rega = None
				cap = None
				if ulaz == 1:
					print ("Čitanje iz kamere 4...")
					cap = cv2.VideoCapture(url_cam4)			
				elif ulaz == 2:
					print ("Čitanje iz kamere 1...")
					cap = cv2.VideoCapture(url_cam1)
				prepkod()
			except:
				print("Prepoznavanje tablice pomoću kamere nije moguće.")
			"""except:
				try:
					rega = None
					cap = None
					if ulaz == 1:
						print ("Čitanje iz kamere 4...")
						cap = cv2.VideoCapture(url_cam4)
					elif ulaz == 2:
						print ("Čitanje iz kamere 1...")
						cap = cv2.VideoCapture(url_cam1)
					prepkod()
				except:
					try:
						rega = None
						cap = None
						if ulaz == 1:
							print ("Čitanje iz kamere 3...")
							cap = cv2.VideoCapture(url_cam3)
						elif ulaz == 2:
							print ("Čitanje iz kamere 2...")
							cap = cv2.VideoCapture(url_cam2)
						prepkod()
					except:
						print("Prepoznavanje registracije pomoću kamere nije moguće.")
						"""


	## Main weighing functions
	def prvo_vaganje():
		global vaganje
		vaganje = 1
		prepoznavanje_tablica()
		if rega == None:
			greska()
		else:
			readcom()
			frega()
			prvo_vaganje2()
	def prvo_vaganje2():
		global rega
		now = datetime.now()
		
		## Categorize image and make dir (if not found) according to plates_categories.py
		klasa_rege = classify(rega)
		vag_prijevoznik = klasa_rege
		if klasa_rege != None:
			img_dir = ('~/SelfWeigh/images_camera/' + klasa_rege + '/')
			if os.path.isdir(img_dir) is False:
				print("Mapa za slike prijevoznika nije pronadjena. Izradjujem novu.")
				dir_path = ("~/SelfWeigh/images_camera/" + klasa_rege + "/")
				os.mkdir(dir_path, 0o777)
				print('Izradjena mapa', '"' + klasa_rege + '".')
				img_dir = ('~/SelfWeigh/images_camera/' + klasa_rege + '/')
		else:
			img_dir = 'images_camera/ostali/'
		
		## Write text on JPG
		cam_dt_string = now.strftime("%Y-%m-%d_%H-%M-%S") + "_" + rega + "_V1" + ".jpg"
		strcomval = str(comvalue)
		rega_img = (" REG: " + rega)
		v1_img =   ("VAG1: " + strcomval + " kg")
		dt_time_img = now.strftime("%d.%m.%Y %H:%M:%S")
		frame2 = cv2.putText(frame, rega_img, org, font, fontScale, color, thickness, cv2.LINE_AA)## Plate
		frame2 = cv2.putText(frame, v1_img, org2, font, fontScale, color, thickness, cv2.LINE_AA)## 1st weight
		frame2 = cv2.putText(frame, dt_time_img, org3, font, fontScale, color, thickness, cv2.LINE_AA)## Timestamp
		full_img_path = img_dir + cam_dt_string
		cv2.imwrite(full_img_path, frame2)## Save JPG to file
		
		print ("img_dir:", img_dir)
		print("cam_dt_string:", cam_dt_string)
		link = upload_slike(img_dir, cam_dt_string)
		
		## Write to CSV
		dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
		with open(csv_remote, 'a', newline='') as file:
			writer = csv.writer(file)
			#			     Plate        Timestamp	     Weight1	   Weight2   Net     Shipper        ImgLink1   ImgLink2
			writer.writerow([str(rega),  str(dt_string), int(comvalue), "null", "null", str(klasa_rege), str(link), "null"])
		print('Upisana registracija:', rega, '\nPrvo vaganje:', comvalue, 'kg', '\n')
		klasa_rege = None
		
		gc.collect()


	def drugo_vaganje():
		global vaganje
		vaganje = 2
		prepoznavanje_tablica()
		if rega == None:
			greska()
		else:
			drugo_vaganje2()
	def drugo_vaganje2():
		global neto
		global vag_neto
		global v1
		global v2
		global vlist
		global comvalue
		
		## Categorize images and make dirs (if not found) according to plates_categories.py 
		klasa_rege = classify(rega)
		vag_prijevoznik = klasa_rege
		if klasa_rege != None:
			img_dir = 'images_camera/' + klasa_rege + '/'
		else:
			img_dir = 'images_camera/ostali/'
		klasa_rege = None
		now = datetime.now()
		cam_dt_string = now.strftime("%Y-%m-%d_%H-%M-%S") + "_" + rega + "_V2" + ".jpg"
		
		## Write to dataframe
		try:
			v1 = None
			v2 = None
			readcom()
			df = pd.read_csv(csv_remote, delim_whitespace=False)
			df2 = df["LicensePlate"].str.endswith(rega, na = False)
			df3 = pd.concat([df[df2]])
			dfnull = df3[df3['Weigh2'].isna()].tail(1)
			index0 = dfnull.index.values
			try:
				vlist = (index0[0] + int(wslip_addend))
			except:
				print("LicensePlate prvog vaganja za drugo vaganje nije pronadjena. Uklanjam zadnje slovo registracije pri pretrazi...")
				rega_shortened = rega[:-1]
				v1 = None
				v2 = None
				df = pd.read_csv(csv_remote, delim_whitespace=False)
				df2 = df["LicensePlate"].str.startswith(rega_shortened, na = False)
				df3 = pd.concat([df[df2]])
				dfnull = df3[df3['Weigh2'].isna()].tail(1)
				index0 = dfnull.index.values
				vlist = (index0[0] + int(wslip_addend))
			dfnull.at[:, 'Weigh2'] = int(comvalue)
			v1 = dfnull.iloc[0]['Weigh1']
			v2 = dfnull.iloc[0]['Weigh2']
			neto = (v1 - v2)
			vag_neto = (v1 - v2)
			dfnull.at[:, 'Net'] = neto
		except:
			print ("Greška; 2. vaganje: CSV upis nije moguć. Otvaranje prozora greške...")
			greska()

		
		## Write on JPG
		v1_img = str(v1)
		v2_img = str(v2)
		neto_img = str (neto)
		
		rega_img = (" REG: " + rega)
		v1_img =   ("VAG1: " + v1_img)
		v2_img =   ("VAG2: " + v2_img)
		neto_img = ("NETO: " + neto_img + " kg")
		dt_time_img = now.strftime("%d.%m.%Y %H:%M:%S")
		
		frame2 = cv2.putText(frame, rega_img, org, font, fontScale, color, thickness, cv2.LINE_AA)## Rega
		frame2 = cv2.putText(frame, v1_img, org2, font, fontScale, color, thickness, cv2.LINE_AA)## V1
		frame2 = cv2.putText(frame, v2_img, org3, font, fontScale, color, thickness, cv2.LINE_AA)## V2
		frame2 = cv2.putText(frame, neto_img, org4, font, fontScale, color, thickness, cv2.LINE_AA)## Net
		frame2 = cv2.putText(frame, dt_time_img, org5, font, fontScale, color, thickness, cv2.LINE_AA)## Timestamp
		
		full_img_path = img_dir + cam_dt_string
		cv2.imwrite(full_img_path, frame2)## Save image locally
		
		## Upload image to GDrive and get image link
		try:
			link = upload_slike(img_dir, cam_dt_string)
			## Write 2nd link to CSV
			dfnull.at[:, 'LinkWEIGH2'] = link
		except:
			print("GRESKA 2. vaganja: Neuspjeli upload slike ili preuzimanja linka na gDrive. Zadnji pokusaj...")
			link = upload_slike(img_dir, cam_dt_string)
			dfnull.at[:, 'LinkWEIGH2'] = link
		link_img = link
		df=df.combine_first(dfnull)
		df.to_csv(csv_remote, index = False)##Save CSV to main server unit
		#df.to_csv(csv_local, index = False)##Save CSV to outdoor unit (backup)
		
		## Save CSV to Google Drive
		try:
			subprocess.Popen(path_csv_to_gdrive)
		except:
			print ("GRESKA 2. vaganje: Neuspjeli upload CSV-a na gDrive. Zadnji pokusaj...")
			subprocess.Popen(path_csv_to_gdrive)
		print('Upisana registracija:', rega, '\nDrugo vaganje:', int(comvalue),'kg', '\n')
	
		## Save vars to vars_local (default vars.py) for further use in Weighslip screen
		with open(vars_local, 'w') as f:
			print('vlist =', '"' + str(vlist) + '"', file=f)
			print('v1 =', v1, file=f)
			print('v2 =', v2, file=f)
			print('vag_neto =', vag_neto, file=f)
			print('vag_rega =', '"' + vag_rega + '"', file=f)
			if vag_prijevoznik != None:
				print('vag_prijevoznik =', '"' + vag_prijevoznik + '"', file=f)
			else:
				print('vag_prijevoznik = None', file=f)
			print('link_img =', '"' + link_img + '"', file=f)
	
		## Cleanup
		del [[df,df2,df3,dfnull]]
		#comvalue = None
		frega2()
		gc.collect()
		df=pd.DataFrame()
		df2=pd.DataFrame()
		df3=pd.DataFrame()
		dfnull=pd.DataFrame()



	def greska():
		def birajvaganje():
			global vaganje
			if vaganje == 1:
				prvo_vaganje()
			if vaganje == 2:
				drugo_vaganje()
		def killgreska():
			win.after(500, lambda:win.destroy())
		win = tk.Toplevel(root)
		win.title("Greška")
		win.attributes('-fullscreen', True)
		#win.attributes('-topmost', True)
		message = 'Tablicu trenutno nije moguće prepoznati.\n Molim pokušajte ponovo ili je ručno unesite.'
		tk.Label(win, text=message, font="Ubuntu\ Condensed 35").pack()
		but = tk.Button(win, height=4, width=15, borderwidth=3, text='Pokušaj ponovo', font="Ubuntu\ Condensed 35 bold", command=lambda:[birajvaganje(), killgreska()])
		but.pack(side=tk.LEFT)
		but2 = tk.Button(win, height=4, width=15, borderwidth=3, text='Ručni unos', font="Ubuntu\ Condensed 35 bold", command=lambda:[tipkovnica("vaganje"), killgreska()])
		but2.pack(side=tk.RIGHT)
		win.after(15000, lambda:win.destroy())
		
	def pitaj():
		win = tk.Toplevel(root)
		win.title("Ispis")
		win.geometry("800x480")
		#root.attributes('-topmost', True)
		#win.attributes('-fullscreen', True)
		message = tk.Label(win, text='Želite li ispis vagarskog lista?', font="Ubuntu\ Condensed 35")
		message.grid(row=0, column=0, columnspan=4, pady=55)
		but = tk.Button(win, height=3, width=10, borderwidth=3, text='Ne', font="Ubuntu\ Condensed 45 bold", command=win.destroy)
		but.grid(row=1, column=0, padx=20)
		def starter():
			subprocess.Popen(pathweighslip)
		def killpitaj():
			win.destroy()
		def countdown(count):
			label['text'] = count
			if count > 0:
				win.after(1000, countdown, count-1)
		label = tk.Label(win, font="Ubuntu\ Condensed 35")
		label.grid(row=1, column=1, padx=20)
		countdown(15)
		win.after(15000, lambda:win.destroy())
		but2 = tk.Button(win, height=3, width=10, borderwidth=3, text='Da', font="Ubuntu\ Condensed 45 bold", command=lambda:[starter(),killpitaj()])
		but2.grid(row=1, column=2, padx=20)
		win.after(15000, lambda:win.destroy())


	def tipkovnica(tipkovnica_vrsta):
		Keyboard_App = tk.Tk()
		Keyboard_App.attributes('-fullscreen', True)
		#Keyboard_App('-topmost', True)
		#Keyboard_App.geometry("800x480")
		def select(value):
			if value == "⌫":
				input = entry.get("1.0", 'end-2c')
				entry.delete("1.0", END)
				entry.insert("1.0", input, END)

			elif value == "ODUSTANI":
				killtipkovnica()
			
			elif value == "POTVRDI":
				if tipkovnica_vrsta is "vaganje":
					global rega
					global vag_rega
					rega0 = entry.get("1.0","end-1c")
					try:
						s = re.search('[A-Z-a-z]{2,2}[0-9]{3,4}[A-Z-a-z]{1,2}', rega0)
						s2 = s.group()
					except: pass
					if s2 == rega0:
						rega = rega0.lower()
						vag_rega = rega0.lower()
						print('Izvoz iz tipkovnice:', rega)
						birajvaganje2()
						killtipkovnica()

					else:
						krivarega = tk.Toplevel(root)
						krivarega.title("Greška")
						message = 'Unijeli ste registraciju u pogrešnom formatu.'
						print ("Incorrect plate format entered")
						tk.Label(krivarega, text=message, font="Ubuntu\ Condensed 20").pack()
						but = tk.Button(krivarega, borderwidth=3, height=3, width=12, text='Pokušaj\nponovo', font="Ubuntu\ Condensed 20 bold", command=krivarega.destroy)
						but.pack(side=tk.BOTTOM)
				
				elif tipkovnica_vrsta is "weighslip":
					unesena_sifra = entry.get("1.0","end-1c")
					unesena_sifra = str(unesena_sifra)
					print("Unesena sifra:", unesena_sifra)
					if unesena_sifra == "2803":
						print("Otvaram weighslip app...")
						subprocess.Popen(pathweighslip_server)
						killtipkovnica()


			else:
				entry.insert(tk.END, value)

		def killtipkovnica():
			Keyboard_App.destroy()

		def birajvaganje2():
			if vaganje == 1:
				readcom()
				prvo_vaganje2()
				frega()
			if vaganje == 2:
				drugo_vaganje2()

		buttons = [
			'1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
			'Q', 'W', 'E', 'R', 'T', 'Z', 'U', 'I', 'O', 'P',
			'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '⌫',
			'Y', 'X', 'C', 'V', 'B', 'N', 'M', 'ODUSTANI', 'POTVRDI',
		]
		if tipkovnica_vrsta is "vaganje":
			entry = Text(Keyboard_App, width=16, height=1, font="Ubuntu 32 bold")
			entry.grid(row=1, columnspan=15)
		elif tipkovnica_vrsta is "weighslip":
			entry = Text(Keyboard_App, width=16, height=1, font="Ubuntu 32 bold")
			entry.grid(row=1, columnspan=15)

		varRow = 2
		varColumn = 0

		for button in buttons:
			command = lambda x=button: select(x)

			if button != "POTVRDI" and button != "ODUSTANI":
				tk.Button(Keyboard_App, text=button, width=2, height=2, font="Ubuntu 27 bold", bg="#000000", fg="#ffffff",
							   activebackground="#ffffff", activeforeground="#000000", relief="raised", padx=13,
							   pady=4, bd=4, command=command).grid(row=varRow, column=varColumn)

			if button == "POTVRDI":
				tk.Button(Keyboard_App, text=button, width=6, font="Ubuntu\ Condensed 12 bold", bg="#20D41B", fg="#ffffff",
							   activebackground="#ffffff", activeforeground="#000000", relief="raised", padx=10,
							   pady=5, bd=4, command=command).grid(row=5, column=9)
							   
			if button == "ODUSTANI":
				tk.Button(Keyboard_App, text=button, width=6, font="Ubuntu\ Condensed 12 bold", bg="#E71E1E", fg="#ffffff",
							   activebackground="#ffffff", activeforeground="#000000", relief="raised", padx=10,
							   pady=5, bd=4, command=command).grid(row=5, column=8)

			varColumn += 1
			if varColumn > 9:
				varColumn = 0
				varRow += 1

	## Main GUI screen
	root = tk.Tk()
	root.geometry("800x380+0+100")
	root.wm_title("WeighEasy")
	root.wm_attributes('-type', 'splash')
	root.attributes('-topmost', False)
	rightframe = tk.Frame(root)
	rightframe.pack(side=tk.RIGHT)

	
	def ponistiregu():
		global rega
		global comvalue
		rega = None
		comvalue = None

	def frega():
		reg1 = tk.Label(rightframe, text="VAGANJE USPJEŠNO\n Nastavite na istovar.\n\n Učitana registracija:", font="Ubuntu\ Condensed 20")
		reg1.grid(row=0, column=0, padx=10, pady=2)
		intRega = tk.IntVar(value=str(rega),)
		reg2 = tk.Label(rightframe, textvariable=intRega, font="Ubuntu\ Condensed 20 bold")
		reg2.grid(row=1, column=0, padx=10, pady=2)
		#readcom()
		intNOW = tk.IntVar(value=(int(comvalue), 'kg'))
		l3 = tk.Label(rightframe, text="Upisana težina: ", font="Ubuntu\ Condensed 20")
		l3.grid(row=5, column=0, padx=10, pady=2)
		l4 = tk.Label(rightframe, textvariable=intNOW, font="Ubuntu\ Condensed 20 bold")
		l4.grid(row=6, column=0, padx=10, pady=2)
		reg1.after(10000, lambda: [reg1.destroy(), ponistiregu()])
		reg2.after(10000, lambda: reg2.destroy())
		l3.after(10000, lambda: l3.destroy())
		l4.after(10000, lambda: l4.destroy())

	def frega2():
		intNet = tk.IntVar(value=("Net:", int(vag_neto), "kg"))
		intRega = tk.IntVar(value=str(rega))
		l1 = tk.Label(rightframe, text="VAGANJE ZAVRŠENO", font="Ubuntu\ Condensed 20")
		l1.grid(row=0, column=0, padx=10, pady=2)
		l2 = tk.Label(rightframe, textvariable=intNet, font="Ubuntu\ Condensed 20 bold")
		l2.grid(row=1, column=0, padx=10, pady=2)
		reg1 = tk.Label(rightframe, text="\n Učitana registracija:", font="Ubuntu\ Condensed 20")
		reg1.grid(row=3, column=0, padx=10, pady=2)
		reg2 = tk.Label(rightframe, textvariable=intRega, font="Ubuntu\ Condensed 20 bold")
		reg2.grid(row=4, column=0, padx=10, pady=2)
		#readcom()
		intNOW = tk.IntVar(value=(int(comvalue), 'kg'))
		l3 = tk.Label(rightframe, text="Upisana težina: ", font="Ubuntu\ Condensed 20")
		l4 = tk.Label(rightframe, textvariable=intNOW, font="Ubuntu\ Condensed 20 bold")
		l4.grid(row=6, column=0, padx=10, pady=2)
		l3.grid(row=5, column=0, padx=10, pady=2)
		reg1.after(4500, lambda: [reg1.destroy(), pitaj()])
		reg2.after(10000, lambda: reg2.destroy())
		l1.after(10000, lambda: l1.destroy())
		l2.after(10000, lambda: l2.destroy())
		l3.after(10000, lambda: l3.destroy())
		l4.after(10000, lambda: [l4.destroy(), ponistiregu()])


	leftframe = tk.Frame(root)
	leftframe.pack(side=tk.LEFT)
	def v1u1():
		global ulaz
		grayout()
		ulaz = 1
		prvo_vaganje()
	def v1u2():
		global ulaz
		grayout()
		ulaz = 2
		prvo_vaganje()
	def v2u1():
		global ulaz
		grayout2()
		ulaz = 1
		drugo_vaganje()
	def v2u2():
		global ulaz
		grayout2()
		ulaz = 2
		drugo_vaganje()

	def v1_man():
		global vaganje
		global frame
		global comvalue
		comvalue = readcom()
		frame = grab_image()
		vaganje = 1
		print ("Rucno vaganje 1")
		tipkovnica("vaganje")
		
	def v2_man():
		global vaganje
		global frame
		frame = grab_image()
		vaganje = 2
		print ("Rucno vaganje 2")
		tipkovnica("vaganje")

	b_font = "Ubuntu\ Condensed 16 bold"
	b_vag_width = 22
	b1 = tk.Button(leftframe,
					   borderwidth='3',
					   text="↑\nPrvo vaganje\n1. ulaz",
					   font=b_font,
					   height=3,
					   width=b_vag_width,
					   command=v1u1)
	b1.grid(sticky=N, row=0, column=0, padx=0, pady=0)
	
	b2 = tk.Button(leftframe,
					   borderwidth='3',
					   text="↓\nPrvo vaganje\n2. ulaz",
					   font=b_font,
					   height=3,
					   width=b_vag_width,
					   command=v1u2)
	b2.grid(sticky=N, row=1, column=0, padx=0, pady=0)
	
	b3 = tk.Button(leftframe,
						borderwidth='3',
					   text="↑\nDrugo vaganje\n1. ulaz",
					   font=b_font,
					   height=3,
					   width=b_vag_width,
					   command=v2u1)
	b3.grid(sticky=N, row=0, column=1, padx=0, pady=0)
	
	b4 = tk.Button(leftframe,
						borderwidth='3',
					   text="↓\nDrugo vaganje\n2. ulaz",
					   font=b_font,
					   height=3,
					   width=b_vag_width,
					   command=v2u2)
	b4.grid(sticky=N, row=1, column=1, padx=0, pady=0)
	
	b5 = tk.Button(leftframe,
						borderwidth='3',
					   text="⌨\nPrvo vaganje\nRučno",
					   font=b_font,
					   height=3,
					   width=b_vag_width,
					   command=v1_man)
	b5.grid(sticky=N, row=2, column=0, padx=0, pady=0)

	b6 = tk.Button(leftframe,
						borderwidth='3',
					   text="⌨\nDrugo vaganje\nRučno",
					   font=b_font,
					   height=3,
					   width=b_vag_width,
					   command=v2_man)
	b6.grid(sticky=N, row=2, column=1, padx=0, pady=0)
	
	b7 = tk.Button(leftframe,
						borderwidth='3',
					   text="Izrada vagarskog lista",
					   font=b_font,
					   height=2,
					   width=47,
					   command=lambda:tipkovnica("weighslip"))
	b7.grid(sticky=N, row=3, column=0,columnspan=2, padx=0, pady=0)
	
	
	# Your contact info at the main screen bottom. Uncomment and edit per your needs.
	#l5=tk.Label(text="www.example.com | example@example.com | +0123456789", font="Ubuntu\ Condensed 8")
	#l5.place(x=5, y=362)
	subprocess.Popen(pathlive)
	root.update()
	root.mainloop()
	
if __name__ == "__main__":
	main()
