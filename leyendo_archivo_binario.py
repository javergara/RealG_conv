import math, struct
import os, mmap
import numpy
import bitstring
import ctypes
import pickle
import array
import binascii


txt_prueba = ('nube_convocatoria.las')
file_txt_prueba = open(txt_prueba ,'rb')
size_txt_prueba = os.path.getsize(txt_prueba )
mapa_prueba = mmap.mmap(file_txt_prueba.fileno(),size_txt_prueba, access=mmap.ACCESS_READ)
print("-----------algunos valores leido del header del archivo .las-----------")
print("-----------------------------------------------------------------------")
print("***********************************************************************")
print("offset points")
#subset = mapa_prueba[3:4]
#values = struct.unpack('<c', subset)#*0.001

subset = mapa_prueba[96:100]
values = struct.unpack('<L', subset)#*0.001
print("valor de offset: ",values)

print("-------------------------longitud del header---------------------------")
print("valor de x: ",bytearray(mapa_prueba[94:96]))
subset = mapa_prueba[94:96]
values = struct.unpack('<H', subset)#*0.001
print("valor de x: ",values)
print("-------leo la version en el emcabezado del archivo---------------------")
print("factor de escala en X: ",bytearray(mapa_prueba[24:26]))
subset = mapa_prueba[24:26]
values = struct.unpack('<2b', subset)
print("version del archivo las: ",values)
print("-----------------id del formato-----------------------")
print("factor de escala en X: ",bytearray(mapa_prueba[104:105]))
subset = mapa_prueba[104:105]
values = struct.unpack('<b', subset)
print("version del formato : ",values)
print("-------factor de escala---------------------")
print("factor de escala en X: ",bytearray(mapa_prueba[131:139]))
subset = mapa_prueba[131:139]
values = struct.unpack('<d', subset)
print("factor de escala en X: ",values)
print("--------------------------------------------")
print("factor de escala en Y: ",bytearray(mapa_prueba[139:147]))
subset = mapa_prueba[139:147]
values = struct.unpack('<d', subset)
print("factor de escala en Y: ",values)
print("--------------------------------------------")
print("factor de escala en Z: ",bytearray(mapa_prueba[147:155]))
subset = mapa_prueba[139:147]
values = struct.unpack('<d', subset)
print("factor de escala en Z: ",values)
print("-----------valores leido del primer bloque del archivo las .las-----------")
print("--------------------------------------------------------------------------")
print("valor de X: ",bytearray(mapa_prueba[227:231]))
subset = mapa_prueba[227:231]
values = struct.unpack('<l', subset)#*0.01
print("valor de X: ",values)
print("--------------------------------------------")
print("valor de Y: ",bytearray(mapa_prueba[231:235]))
subset = mapa_prueba[231:235]
values = struct.unpack('<l', subset)#*0.01
print("valor de Y: ",values)
print("--------------------------------------------")
print("valor de Z: ",bytearray(mapa_prueba[235:239]))
subset = mapa_prueba[235:239]
values = struct.unpack('<l', subset)#*0.01
print("valor de Z: ",values)
print("--------------------------------------------")
print("valor de ID: ",bytearray(mapa_prueba[246:248]))
subset = mapa_prueba[300:302]
values = struct.unpack('<H', subset)
print("valor de ID: ",values)
print("--------------------------------------------")
print("valor de tiempo: ",bytearray(mapa_prueba[248:256]))
subset = mapa_prueba[247:255]
values = struct.unpack('<d', subset)
print("valor de tiempo: ",values)
