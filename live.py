#!/usr/bin/python3

import tkinter as tk
import serial, re, os
from settings_main import serial_port, serial_baud, tracker_local
from datetime import datetime
displayison = False
lastwritten = 10

def main():
    root = tk.Tk()
    root.geometry("800x100+0-400")
    root.wm_attributes('-type', 'splash')
    bruto = tk.Label(root, text="Trenutna težina (bruto):", font="Ubuntu\ Condensed 41 bold")
    bruto.place(x=5, y=58, anchor="w")
    status = tk.Label(root, text="n", font="Ubuntu\ Condensed 41 bold")
    status.place(x=790, y=58, anchor="e")
    displayison = False
    lastwritten = 100
    #global file1
    #file1 = open("tracker.txt","a")
    
    def update_status():
        ser = serial.Serial(serial_port, serial_baud)
        cc=str(ser.readline().decode())
        comvalue0=re.search('[0-9]{2,5}', cc)
        try:
            comvalue = comvalue0.group()
        except:
            comvalue = "00"
        # Update the message
        status["text"] = (comvalue, "kg")
        comvalue = int(comvalue)
        # Turn on display if min_weight_cond larger than set value
        min_weight_cond = comvalue > 120
        global displayison
        global lastwritten
        if (displayison is False and comvalue > 120):
            os.system("DISPLAY=:0 xset dpms force on")
            displayison = True
        elif (displayison is True and comvalue > 120):
            displayison = True
        elif (displayison is True and comvalue < 120):
            displayison = False
        #    try:
        #        os.system("killall weighslip.py")
        #    except:
        #        pass
            os.system("DISPLAY=:0 xset dpms force off")
            
        now = datetime.now()
        dt_string = now.strftime("%d.%m.%Y. %H:%M:%S")
        #strcom = str(comvalue)
        #global file1
        #if file1.closed is True:
        #    file1 = open("tracker.txt","a")
        
        if min_weight_cond is True and comvalue != lastwritten:
            with open(tracker_local, 'a') as ff:
                print(str(dt_string), str(comvalue), file=ff)
               # print(str(comvalue), file=ff)
        #file1.write(dt_string)
        #file1.write(strcom)
        lastwritten = int(comvalue)

        root.after(1250, update_status)


    root.after(2000, update_status)
    root.update()
    root.mainloop()
    
if __name__ == "__main__":
    main()
