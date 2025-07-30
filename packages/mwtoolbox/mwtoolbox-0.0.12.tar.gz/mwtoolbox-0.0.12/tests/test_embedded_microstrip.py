from mwtoolbox.rfnetwork import *
import mwtoolbox.transmission_lines as tline

w = 25*25.4e-6
h1 = 10*25.4e-6
h2 = 15*25.4e-6
er = 3
t = 1*25.4e-6

z1 = tline.z_qs_thick_embedded_microstrip_1(w, h1, h2, er, t)

z2 = tline.z_qs_thick_embedded_microstrip(w, h1, h2, er, t)

print(f"{z1=}")
print(f"{z2=}")
