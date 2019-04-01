import brother_ql
import brother_ql.backends
import brother_ql.backends.helpers
import brother_ql.backends.pyusb
import os


image = os.getcwd() + '/barcode.png'
ql_printer = brother_ql.BrotherQLRaster(model='QL-500')
ql_printer.cut_at_end = False
brother_ql.create_label(ql_printer, image, label_size='12', cut=False, dither=True, compress=False, red=False, rotate=90)

printer = brother_ql.backends.pyusb.list_available_devices()[0]['identifier']
# be = brother_ql.backends.backend_factory('pyusb')['backend_class']('usb://0x04f9:0x2015')
print(printer)
# print(brother_ql.backends.pyusb.list_available_devices())
# brother_ql.backends.helpers.discover(backend_identifier='pyusb')
brother_ql.backends.helpers.send(ql_printer.data, printer_identifier=printer, backend_identifier='pyusb')
# brother_ql.backends.helpers.send(instructions=ql_printer.data, printer_identifier=printer, backend_identifier='pyusb', blocking=True)

print(image)