import math, struct
from open3d import *
import numpy as np
import bitstring
import ctypes
import pickle
import array
import binascii
import os, mmap

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

	data_point = [las_values['x'],las_values['y'],las_values['z']]
	return data_point

#@count_elapsed_time
def points_matrix(mapa_las, n_points):
	"""
	Returns a matrix:
	Matrix = [[x_1,y_1,z_1],...,[x_n, y_n, z_n]] , n= total points
	"""
	total_points = num_datagrams(mapa_las,28,227)
	if n_points <= total_points:
		step = int(total_points/n_points)
		matrix=([read_packets_las(i,mapa_las) for i in range(0,total_points, step)])
	else:
		matrix=([read_packets_las(i,mapa_las) for i in range(0,total_points)])
	return matrix

def dibujar(matrix,flag):
	"""
	Converts a matrix into a point cloud object and draw de points
	"""
	if flag == 0:
		xyz=Vector3dVector(matrix)
		pcd = PointCloud()
		pcd.points = (xyz)

		#("Downsample the point cloud with a voxel of 0.02")
		voxel_down_pcd = voxel_down_sample(pcd, voxel_size = 0.02)

		#("Every 5th points are selected")
		uni_down_pcd = uniform_down_sample(pcd, every_k_points = 5)
		mesh_frame = create_mesh_coordinate_frame(size = 60, origin = [664804.83, 454351.78, 349.61])
		draw_geometries([pcd , mesh_frame])
	elif flag == 1:
		pcd = read_point_cloud(matrix)
		draw_geometries([pcd])



def read_ply_points(url):
	pcd = read_point_cloud(url)
	return (str(pcd)[15:23])

def read_file(direccion):
	file_las = (direccion)
	las_file = open(file_las,'rb')
	las_size = os.path.getsize(file_las)
	mapa_las = mmap.mmap(las_file.fileno(),las_size, access=mmap.ACCESS_READ)
	return mapa_las
