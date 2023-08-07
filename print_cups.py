#!/usr/bin/python3

from fpdf import FPDF
import pyqrcode, png
import os
from datetime import datetime
from vars_print import *

def main():
	pdf_font = 'Hack'
	pdf = FPDF('P', 'mm',  (58,105))
	pdf.set_left_margin(5)
	pdf.set_right_margin(5)
	pdf.set_top_margin(5)
	pdf.set_auto_page_break(False, 0.5)
	#pdf.set_footer_margin(3)
	#pdf.add_page()
	pdf.add_page()
	pdf.add_font('Hack', '', '/usr/share/fonts/truetype/hack/Hack-Regular.ttf', uni=True)
	pdf.add_font('Hack', 'B', '/usr/share/fonts/truetype/hack/Hack-Bold.ttf', uni=True)

	#pdf.cell(40, 10, 'Hello World!')


	#pdf = FPDF(orientation = 'P', unit = 'mm', format='58x80')

	#vlist = 500
	#v1 = 20000
	#v2 = 15000
	#vag_neto = 5000
	#roba = "biootpad"
	#rega = "vz121xx"
	#vag_rega = "vz121xx"
	#prijevoznik = "otpad-prevoz"
	#vozac = "miroooooooooooo"
	#prodavac = "otpadi otpadi"
	#kupac = "YourCompany, Some  description"
	#dt_string = "21.09.2020         19:20:25"
	#link_img = "https://docs.google.com/uc?export=download&id=..............."
	
	test_dt = 'dt_string' in globals()
	if test_dt is False:
		now = datetime.now()
		dt_string2 = now.strftime("%d.%m.%Y.        %H:%M:%S")
	else:
		dt_string2 = dt_string

	qr_code = pyqrcode.create(link_img, error='M', version=5, mode='binary')
	qr_code.png('code.png', scale=1, module_color=[0, 0, 0, 126], background=[0xFF, 0xFF, 0xFF])


	str_vlist = str(vlist)
	str_v1 = str(v1) + " kg"
	str_v2 = str(v2) + " kg"
	str_vag_neto = str(vag_neto) + " kg"

	lheight = 3

	pdf.image("~/SelfWeigh/your-logo.png", x = 11, y = None, w = 35, h = 10, type = 'png', link = '')

	pdf.set_font(pdf_font, '', 7)
	pdf_uvod = "Short company description\nAaddress\nCity\nwww.example.com\n\n"


	pdf.multi_cell(0, 2.8, pdf_uvod, 0, 'C', False)

	pdf.set_font(pdf_font, '', 8)	                	## Font size + 1

	pdf.multi_cell(0, 4, dt_string2, 0, 'L', False)

	pdf.multi_cell(0, 1, '---------------------------', 0, 'L', False)

	pdf.cell(32, 4, 'Vagarski list br.: ',   0, 0, 'L', False, '')
	pdf.multi_cell(15, 4, str_vlist, 0, 'R', False)

	pdf.cell(21, 4, 'Vaganje 1:',   0, 0, 'L', False, '')
	pdf.multi_cell(26, 4, str_v1, 0, 'R', False)

	pdf.cell(21, 4, 'Vaganje 2:',   0, 0, 'L', False, '')
	pdf.multi_cell(26, 4, str_v2, 0, 'R', False)

	pdf.set_font(pdf_font, 'B', 8)                    ## Bold font
	pdf.cell(21, 4,  'Net:',       0, 0, 'L', False, '')
	pdf.multi_cell(26, 4, str_vag_neto, 0, 'R', False)

	pdf.set_font(pdf_font, '', 8)                     ## No bold
	pdf.multi_cell(0, 1, '---------------------------', 0, 'L', False)

	pdf.set_font(pdf_font, 'B', 8)
	pdf.cell(21, 4, 'Vrsta robe:',  0, 0, 'L', False, '')
	pdf.set_font(pdf_font, '', 8)
	pdf.multi_cell(26, 4, roba, 0, 'R', False)

	pdf.set_font(pdf_font, 'B', 8)
	pdf.cell(21, 4, 'LicensePlate:',0, 0, 'L', False, '')
	pdf.set_font(pdf_font, '', 8)
	pdf.multi_cell(26, 4, vag_rega, 0, 'R', False)

	pdf.set_font(pdf_font, 'B', 8)
	pdf.cell(21, 4, 'Shipper:', 0, 0, 'L', False, '')
	pdf.set_font(pdf_font, '', 8)
	pdf.multi_cell(26, 4, prijevoznik, 0, 'R', False)

	pdf.set_font(pdf_font, 'B', 8)
	pdf.cell(21, 4,    'Vozač:',    0, 0, 'L', False, '')
	pdf.set_font(pdf_font, '', 8)
	pdf.multi_cell(26, 4, vozac, 0, 'R', False)

	pdf.set_font(pdf_font, 'B', 8)
	pdf.cell(21, 4,   'Prodavač:',  0, 0, 'L', False, '')
	pdf.set_font(pdf_font, '', 8)
	pdf.multi_cell(26, 4, prodavac, 0, 'R', False)

	pdf.set_font(pdf_font, 'B', 8)
	pdf.cell(21, 4, 'Kupac/Preuz:',0, 0, 'L', False, '')
	pdf.set_font(pdf_font, '', 8)
	pdf.multi_cell(26, 4, kupac, 0, 'R', False)

	pdf.image('code.png', x = None, y = None, w = 15, h = 15, type = 'png', link = '')

	pdf.set_xy(25, 93)
	pdf.set_font(pdf_font, '', 5)
	pdf.multi_cell(0, 2, "Scan QR code to view E-Weighslip.", 0, 'R', False)

	save_dir = '~/SelfWeigh/weighslips/' + vlist + '.pdf'
	pdf.output(save_dir, 'F')
	
	os_komanda = 'lp -d POS58 ' + save_dir
	os.system(os_komanda)

if __name__ == "__main__":
	main()
