from mwtoolbox.rfnetwork import *
import mwtoolbox.transmission_lines as tline

arg = ["300um","127um","35um","3.66","0.0018","0.1","5e7","1.0","5um","77e9","1mm","130.0","100","100"]

sonuc = tline.microstrip_synthesis(arg, [])

print(sonuc)
# h=0.127
# print(tline.z_qs_thin_microstrip(h*1e-11, h, 3.66))