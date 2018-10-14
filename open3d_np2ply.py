import copy
import numpy as np
from open3d import *
import math, struct
import os, mmap
import numpy
import bitstring
import ctypes
import pickle
import array
import binascii
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import numpy as np
from time import time

def count_elapsed_time(f):
	"""
	Decorator.
	Execute the function and calculate the elapsed time.
	Print the result to the standard output.
	"""
	def wrapper():
		# Start counting.
		start_time = time()
		# Take the original function's return value.
		ret = f()
		# Calculate the elapsed time.
		elapsed_time = time() - start_time
		print("Elapsed time: %0.10f seconds." % elapsed_time)
		return ret

	return wrapper


def num_datagrams(data,datagram_size ,rest=0):
	longi = len(data)-rest
	#assert(longi%datagram_size== 0)
	return int(longi / datagram_size)

def estructura_las(value):
	if value == 1:
		file_las = ('x','y','z','intensidd','4en1',\
			'clasificacion','anguloescaneo','userdata','#punto','gpstime')
	else:
		print("Error en el valor de entrada de la función estructura_las")
	return file_las

def deco_las(value):
	if value == 1:
		decobytes = '<lllHbBBBHd'
		'''
		POINT DATA RECORD FORMAT 1:
		x ---------------------------------------- file_las['x'] -------------l
		y ---------------------------------------- file_las['y'] -------------l
		z ---------------------------------------- file_las['z'] -------------l
		intensity -------------------------------- file_las['intensidd'] -----H
		return Number ---------------------------- \
		Number of return(given pulse) ------------  \
		scan direction flag ----------------------  /  file_las['4en1'] ------b
		edge of flight line ---------------------- /____________________
		classification --------------------------- file_las['clasificacion'] -B
		scan anfle rank (-90 to +90) -left side -- file_las['anguloescaneo'] -B
		user data -------------------------------- file_las['userdata'] ------B
		point sourse ID -------------------------- file_las['#punto'] --------H
		GPS time --------------------------------- file_las['gpstime'] -------d
		'''
	else:
		print("Error en el valor ingresado a deco_las")
	return decobytes

def read_packets_las(packet,mapa):
	if packet >= 0:
		offset = 227 + (28*(packet))
		datagram_size = 28
		numdeco = 1
	else:
		print("error en dato block función read_packets_las")

	subset = mapa[ offset :  offset + datagram_size ]
	values = struct.unpack(deco_las(numdeco), subset)
	las_values = dict(list(zip (estructura_las(numdeco) , values)))
	#busco en el header los factores de escala de xyz
	coordenadas_xyz = ('x','y','z')
	subset = mapa[ 131 :  155 ]
	values = struct.unpack('<3d', subset)
	escala_values = dict(list(zip (coordenadas_xyz , values)))
	#busco en el header los factores de offset de xyz
	subset = mapa[ 155 :  179 ]
	values = struct.unpack('<3d', subset)
	offset_values = dict(list(zip (coordenadas_xyz , values)))
	#multiplico x por su factor de escala

	las_values['x'] = las_values['x'] * escala_values['x']
	#multiplico y por su factor de escala
	las_values['y'] = las_values['y'] * escala_values['y']
	#multiplico z por su factor de escala
	las_values['z'] = las_values['z'] * escala_values['z']
	#le suma a x su respectivo offset
	las_values['x'] = las_values['x'] + offset_values['x']
	#le suma a y su respectivo offset
	las_values['y'] = las_values['y'] + offset_values['y']
	#le suma a z su respectivo offset
	las_values['z'] = las_values['z'] + offset_values['z']

	#data_point = np.array([las_values['x'],las_values['y'],las_values['z']])
	data_point = [las_values['x'],las_values['y'],las_values['z']]
	return data_point

file_las = ('nube_convocatoria.las')
las_file = open(file_las,'rb')
las_size = os.path.getsize(file_las)
mapa_las = mmap.mmap(las_file.fileno(),las_size, access=mmap.ACCESS_READ)
las_values = read_packets_las(414912,mapa_las) #se solicitan los datos del packet 0 del archivo de nube de puntos
print("valores en el primer paquete del archivo nube_convocatoria.las")
print(las_values)
print("-------numero de puntos en el las---------------------")
print(num_datagrams(mapa_las,28,227))

def test1():
	#for i in range((num_datagrams(mapa_las,28,227))):
	matriz=([read_packets_las(i,mapa_las) for i in range(0,10000000)])
	return matriz
# 36478801

#@count_elapsed_time
def test():
	matriz = np.append([(read_packets_las(i,mapa_las)) for i in range(0,1000)])
	#xyz=Vector3dVector(matriz)
	#xyz= Vector3dVector(matriz)
	#print('termino for test1(rapido)')
	print (matriz)
	return matriz

xyz= test1()
xyz=Vector3dVector(xyz)
pcd = PointCloud()
pcd.points = (xyz)
# Pass xyz to Open3D.PointCloud and visualize
#pcd = PointCloud()
#pcd.points = (test())

draw_geometries([pcd])
