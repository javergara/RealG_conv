import math, struct
import os, mmap
import numpy
import bitstring
import ctypes
import pickle
import array
import binascii

def num_datagrams(data,datagram_size ,rest=0):
	longi = len(data)-rest
	#assert(longi%datagram_size== 0)
	return int(longi / datagram_size)

def estructura_las(value):
	if value == 1:
		file_las = ('x','y','z','intensidd','4en1',\
			'clasificacion','anguloescaneo','userdata','#punto','gpstime')
	elif value == 2:
		'''
		en este espacio pueden agregar para leer algunos datos del "header" si gustan
		pero por tiempo recomiendo leer los datos que neceten de la forma en que se encuentra
		en el script (leyendo_archivo_binario.py)
		'''
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
	elif value == 2:
		'''
		en este espacio agregan la estructura en bytes para leer el header si lo requieren, pero nuevamente recomiendo
		leer los datos del header como en el script (leyendo_archivo_binario.py) por temas de tiempo. pero si desean leerlo
		como el resto del archivo recomiendo utilizar como referencia la tabla mostrada en
		https://docs.python.org/3.4/library/struct.html#struct.error
		'''
	else:
		print("Error en el valor ingresado a deco_las")
	return decobytes

def read_packets_las(packet,mapa):
	'''
	si desean agregar la lectura del header seria de esta forma
	if packet >= 1: # tener en cuenta que el primer packete en la numeracion interna (point sourse ID) es cero
		offset = 227 + (28*(packet))
		datagram_size = 28
		numdeco = 1
	elif packet == 0:
		offset =0
		datagram_size = 227
		numdeco = 2
	'''
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
	'''
	si requieren algun dato del header aconsejo leerlo como en este script se leen los offset y
	los factores de escala ya que de leer el header como se leen los packets tomaria muhco tiempo
	en implementar
	'''
	return las_values


def main():
	file_las = ('nube_convocatoria.las')
	las_file = open(file_las,'rb')
	las_size = os.path.getsize(file_las)
	mapa_las = mmap.mmap(las_file.fileno(),las_size, access=mmap.ACCESS_READ)
	las_values = read_packets_las(414912,mapa_las) #se solicitan los datos del packet 0 del archivo de nube de puntos
	print("valores en el primer paquete del archivo nube_convocatoria.las")
	print(las_values)
	print("xxxx")
	print(las_values['x'])
	las_values = read_packets_las(1,mapa_las) #se solicitan los datos del packet 1 del archivo de nube de puntos
	print("valores en el segundo paquete del archivo nube_convocatoria.las")
	print(las_values)
	print("-------numero de puntos en el las---------------------")
	print(num_datagrams(mapa_las,28,227))
	print("-------confirmo resultado leyendo el archivo directamente---------")
	subset = mapa_las[ 107 : 111 ]
	values = struct.unpack('<L', subset)
	print("numero de registro de puntos dentro del archivo : ",values)
	x=[]
	y=[]
	z=[]
	#for i in range((num_datagrams(mapa_las,28,227))):
	for i in range(1000):
		las_values = read_packets_las(i,mapa_las)
		x.append(las_values['x'])
		y.append(las_values['y'])
		z.append(las_values['z'])

	print('termino for')

	from mpl_toolkits.mplot3d import Axes3D
	import matplotlib.pyplot as plt
	import numpy as np


	def randrange(n, vmin, vmax):
	    '''
	    Helper function to make an array of random numbers having shape (n, )
	    with each number distributed Uniform(vmin, vmax).
	    '''
	    return (vmax - vmin)*np.random.rand(n) + vmin

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	n = 100

	# For each set of style and range settings, plot n random points in the box
	# defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
	#for c, m, zlow, zhigh in [('r', 'o', -50, -25), ('b', '^', -30, -5)]:
	 #  xs = randrange(n, 23, 32)
	  #  ys = randrange(n, 0, 100)
	  #  zs = randrange(n, zlow, zhigh)
	ax.scatter(x, y, z, marker= 'o')

	ax.set_xlabel('X Label')
	ax.set_ylabel('Y Label')
	ax.set_zlabel('Z Label')

	plt.show()


if __name__=='__main__':
	main()
