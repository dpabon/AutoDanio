#F(u,v,w)  Limits of pruduction susbstances U, V, W
import numpy as np
import matplotlib.pyplot as plt
#%matplotlib inline
#los valores para definir los limites de la funcion de f [U,V] son tomados
# de la literatura, esto a asegura que las concentraciones no tomen valores realistas en la posicion actual.

def ratesU (UC,c1v,c2w,c3):    # UC = [U] inicial
    if c1v+c2w+c3 < 0:
        UC= 0
    elif 0< c1v+c2w+c3 < UC:
        UC= c1v+c2w+c3
    else:
        UC= UC
    print UC
    return UC,c1v,c2w,c3


def ratesV (VC,c4u,c5w,c6): #VC =   [V] inicial

    if c4u + c5w +c6 < 0:
        VC = 0
    elif 0< c4u + c5w +c6 < VC:
        VC = c4u + c5w +c6
    else:
        VC = VC
    print VC
    return VC,c4u,c5w,c6


Urates = ratesU (0.5,0.04,0.055,0.37)

Vrates = ratesV (0.5,0.05,0.0,0.25)
