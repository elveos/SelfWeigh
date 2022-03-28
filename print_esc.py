#!/usr/bin/python3

from escpos.printer import Usb
from escpos.printer import Dummy
from vars import file_name, link_img
from escpos import printer

def main():
file_name2 = str(file_name)
link_img2 = str(link_img)
p = printer.Usb(0x0416, 0x5011, 4, in_ep=0x81, out_ep=0x03)
d = Dummy()
d.image("your-logo.bmp")
d.text(file_name2)
d.qr(link_img2)
d.text("Scan QR code\n to view E-Weighslip.\n\n\n ")
d.cut()
p._raw(d.output)
	p.hw("RESET")
if __name__ == "__main__":
	main()
 
