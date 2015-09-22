#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 11:30:30 2015
@author: user
"""

##################################################################
#                  Librerias Necesarias                          #
##################################################################
#from scipy import misc
from scipy import ndimage
import numpy as np
import matplotlib.pyplot as plt
import cv2
import random
import sys
import os
import time


################################################################ 
#                 Definición de funciones                      #
################################################################

# Conversión a escala de grises
def esgri(imagen):
    imagen=cv2.cvtColor(imagen, cv2.COLOR_RGB2GRAY )
    return imagen

# Normalización de la imagen escala 0:1
def normalizacion(x):
    a = []
    for pixel in np.nditer(x):
        b=float(pixel)/x.max()
        a.append(b)
  
    B = np.reshape(a, (len(x),len(x)))
    return B

# Reajuste de la imagen para disminuir el ruido de la misma
def reajuste(x):
    for pixel in np.nditer(x, op_flags=['readwrite']):
        if pixel>0.75:
            pixel[...]=1
        else:
            pixel[...]=pixel
        if pixel<0.7:
            pixel[...]=random.uniform(0.1,0.4)
        else:
            pixel[...]=pixel
    return x


## Parametros iniciales propuestos por Nakamasu et al.2009
cmsp = 2      # Tasa de producción de Ms
cmsd = 0.2    # Tasa de decaimiento de Ms
dms = 0.015   # Tasa de difusion de Ms
cxsp = 2      # Tasa de producción de Xs
cxsd = 0.2    # Tasa de decaimiento de Xs
dxs = 0.015   # Tasa de difusion de Xs
cxlp = 2.8    # Tasa de producción de Xl
cxld = 0.2    # Tasa de decaimiento de Xl
dxl = 0.3     # Tasa de difusion de Xl
c1 = 1.5      
c2= 15
c3= 11
c4 = 1.5
cmdths = 3
cxdths = 2.2
cmdthl = 3.0
cmapps = 1
cxapps = 1
cmappl = 0.6
pmapp = 0.005
pxapp = 0.2
pmdth = 0.8
pxdth = 0.8
cmdthl = 5


#This board possesses a 0 border that allows to accelerate things a bit by avoiding to have specific tests for 
#borders when counting the number of neighbours. First step is to count neighbours:

def compute_neigbours(image_final):
    image_final.astype(int)
    shape = len(image_final), len(image_final[0])
    N  = [[0,]*(shape[0])  for i in range(shape[1])]
    for x in range(1,shape[0]-1):
        for y in range(1,shape[1]-1):
            N[x][y] = image_final[x][y-1] \
                    + image_final[x-1][y]            +image_final[x+1][y]   \
                    + image_final[x][y+1]
            
                 
    return N

# Determinación de la concentración de ms (sustancia producida por los melanoforos)

def delta_ms (image_final):
    N=compute_neigbours(image_final)
    shape = len(image_final), len(image_final[0])
    ms  = [[0,]*(shape[0])  for i in range(shape[1])]
    for r in range(1,shape[0]-1):
        for s in range(1,shape[1]-1):
            if ms[r][s]<0.2:
                ms[r][s] = (((cmsp * image_final[r][s]) - (cmsd * image_final[r][s])) \
                        + (dms * (N[r][s] - (4* image_final[r][s]))))
            else:
                ms[r][s]==ms[r][s]
            
    return ms


#Cambio en la producción de la sustancia XS, producida por xantoforos

def delta_xs (image_final):
    N=compute_neigbours(image_final)
    shape = len(image_final), len(image_final[0])
    xs  = [[0,]*(shape[0])  for i in range(shape[1])]    
    for r in range(1,shape[0]-1):
        for s in range(1,shape[1]-1):
            if 0.4>xs[r][s]>0.2:
                xs[r][s] = (((cxsp * image_final[r][s]) - (cxsd * image_final[r][s])) \
                        + (dxs * (N[r][s] - (4* image_final[r][s]))))
            else:
                xs[r][s]=xs[r][s]
    return xs

#cambio de produccion de la sustancia xl, producida por xantoforos
def delta_xl (image_final):
    N=compute_neigbours(image_final)
    shape = len(image_final), len(image_final[0])
    xl  = [[0,]*(shape[0])  for i in range(shape[1])]
    for r in range(1,shape[0]-1):
        for s in range(1,shape[1]-1):
            if 0.4>xl[r][s]>0.2:
                xl[r][s] = (((cxlp * image_final[r][s]) - (cxld * image_final[r][s])) \
                        + (dxl * (N[r][s] - (4* image_final[r][s]))))
    return xl

#Comportamiento celular de rango corto para los melanoforos
def mshort (image_final):
    xs= delta_xs (image_final)
    ms= delta_ms (image_final)
    shape = len(image_final), len(image_final[0])
    mshort  = [[0,]*(shape[0])  for i in range(shape[1])]
    
    for r in range(1,shape[0]-1):
        for s in range(1,shape[1]-1):
            mshort[r][s] = ((c1 * ms[r][s])+ (c2 * xs[r][s]))
    return mshort

#Comportamiento celular de rango corto para los xantoforos
def xshort (image_final):
    xs= delta_xs (image_final)
    ms= delta_ms (image_final)
    shape = len(image_final), len(image_final[0])
    xshort  = [[0,]*(shape[0])  for i in range(shape[1])]
    for r in range(1,shape[0]-1):
        for s in range(1,shape[1]-1):
            xshort[r][s] = ((c3 * ms[r][s])+ (c4 * xs[r][s]))
    return xshort

###############################################################################
##                           Bienvenida                                      ##
###############################################################################

Titulo="""                _        _____              _       
     /\        | |      |  __ \            (_)      
    /  \  _   _| |_ ___ | |  | | __ _ _ __  _  ___  
   / /\ \| | | | __/ _ \| |  | |/ _` | '_ \| |/ _ \ 
  / ____ \ |_| | || (_) | |__| | (_| | | | | | (_) |
 /_/    \_\__,_|\__\___/|_____/ \__,_|_| |_|_|\___/ 
                                                    """                                    
Autores="Creado por: Juan Seco y Daniel Pabón"
web="https://github.com/jjseco/AutoDanio"
Subtitulo1="""Bienvenido a AutoDanio""" 
Subtitulo2="""Autómata celular para crear patrones de coloración de pez cebra"""
Subtitulo3="""Por favor presione "s" para continuar o "n" para salir"""
print Titulo.center(50, "*")
print Autores.center(50, "*")
print web.center(50, "*")
print " "
print Subtitulo1.center(50, "*")
print Subtitulo2.center(50, "*")
print (" ")
print Subtitulo3.center(50, "*")
Primer_entrada=raw_input()
if Primer_entrada=="n":
    print ("Que tenga un buen dia")
    sys.exit(0)
else:
    print ("Para continuar necesita una imagen de la banda lateral de pez cebra digite el nombre de la imagen con su respectivo directorio")
    pass
# Cambie por la imagen a procesar
directorio=raw_input()
danio= cv2.imread(directorio)
print "La imagen actual es:"
cv2.imshow('image',danio)
cv2.waitKey(0)
cv2.destroyAllWindows()
time.sleep(5.0)
print " "
print "Para continuar procesaremos la imagen a escala de grises, Cierre la ventana de la imagen"
grises=raw_input()

print "Todo bien"
