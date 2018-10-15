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
from open3d import *
################################################################################
import matplotlib.pyplot as plt

def custom_draw_geometry(pcd):
	# The following code achieves the same effect as:
	# draw_geometries([pcd])
	vis = Visualizer()
	vis.create_window()
	vis.add_geometry(pcd)
	vis.run()
	vis.destroy_window()

def custom_draw_geometry_with_custom_fov(pcd, fov_step):
	vis = Visualizer()
	vis.create_window()
	vis.add_geometry(pcd)
	ctr = vis.get_view_control()
	print("Field of view (before changing) %.2f" % ctr.get_field_of_view())
	ctr.change_field_of_view(step = fov_step)
	print("Field of view (after changing) %.2f" % ctr.get_field_of_view())
	vis.run()
	vis.destroy_window()

def custom_draw_geometry_with_rotation(pcd):
	def rotate_view(vis):
		ctr = vis.get_view_control()
		ctr.rotate(10.0, 0.0)
		return False
	draw_geometries_with_animation_callback([pcd], rotate_view)

def custom_draw_geometry_load_option(pcd):
	vis = Visualizer()
	vis.create_window()
	vis.add_geometry(pcd)
	vis.get_render_option().load_from_json(
			"../../TestData/renderoption.json")
	vis.run()
	vis.destroy_window()

def custom_draw_geometry_with_key_callback(pcd):
	def change_background_to_black(vis):
		opt = vis.get_render_option()
		opt.background_color = np.asarray([0, 0, 0])
		return False
	def load_render_option(vis):
		vis.get_render_option().load_from_json(
				"../../TestData/renderoption.json")
		return False
	def capture_depth(vis):
		depth = vis.capture_depth_float_buffer()
		plt.imshow(np.asarray(depth))
		plt.show()
		return False
	def capture_image(vis):
		image = vis.capture_screen_float_buffer()
		plt.imshow(np.asarray(image))
		plt.show()
		return False
	key_to_callback = {}
	key_to_callback[ord("K")] = change_background_to_black
	key_to_callback[ord("R")] = load_render_option
	key_to_callback[ord(",")] = capture_depth
	key_to_callback[ord(".")] = capture_image
	draw_geometries_with_key_callbacks([pcd], key_to_callback)

def custom_draw_geometry_with_camera_trajectory(pcd):
	custom_draw_geometry_with_camera_trajectory.index = -1
	custom_draw_geometry_with_camera_trajectory.trajectory =\
			read_pinhole_camera_trajectory(
					"../../TestData/camera_trajectory.json")
	custom_draw_geometry_with_camera_trajectory.vis = Visualizer()
	if not os.path.exists("../../TestData/image/"):
		os.makedirs("../../TestData/image/")
	if not os.path.exists("../../TestData/depth/"):
		os.makedirs("../../TestData/depth/")
	def move_forward(vis):
		# This function is called within the Visualizer::run() loop
		# The run loop calls the function, then re-render
		# So the sequence in this function is to:
		# 1. Capture frame
		# 2. index++, check ending criteria
		# 3. Set camera
		# 4. (Re-render)
		ctr = vis.get_view_control()
		glb = custom_draw_geometry_with_camera_trajectory
		if glb.index >= 0:
			print("Capture image {:05d}".format(glb.index))
			depth = vis.capture_depth_float_buffer(False)
			image = vis.capture_screen_float_buffer(False)
			plt.imsave("../../TestData/depth/{:05d}.png".format(glb.index),\
					np.asarray(depth), dpi = 1)
			plt.imsave("../../TestData/image/{:05d}.png".format(glb.index),\
					np.asarray(image), dpi = 1)
			#vis.capture_depth_image("depth/{:05d}.png".format(glb.index), False)
			#vis.capture_screen_image("image/{:05d}.png".format(glb.index), False)
		glb.index = glb.index + 1
		if glb.index < len(glb.trajectory.extrinsic):
			ctr.convert_from_pinhole_camera_parameters(glb.trajectory.intrinsic,\
					glb.trajectory.extrinsic[glb.index])
		else:
			custom_draw_geometry_with_camera_trajectory.vis.\
					register_animation_callback(None)
		return False
	vis = custom_draw_geometry_with_camera_trajectory.vis
	vis.create_window()
	vis.add_geometry(pcd)
	vis.get_render_option().load_from_json("../../TestData/renderoption.json")
	vis.register_animation_callback(move_forward)
	vis.run()
	vis.destroy_window()
#######################################################################
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

@count_elapsed_time
def points_matrix():
	"""
	Returns a matrix:
	Matrix = [[x_1,y_1,z_1],...,[x_n, y_n, z_n]] , n= total points

	For getting the total amount of points the parameter in the for cycle is:
	range(0,num_datagrams(mapa_las,28,227))

	"""
	matrix=([read_packets_las(i,mapa_las) for i in range(0,36000000,10000)])
	return matrix

def dibujar(matrix):
	xyz=Vector3dVector(matrix)
	pcd = PointCloud()
	pcd.points = (xyz)
	downpcd = voxel_down_sample(pcd, voxel_size = 5)
	#draw_geometries([downpcd])
	#draw_geometries([pcd])
	mesh_frame = create_mesh_coordinate_frame(size = 60, origin = [665004.83, 454351.78, 349.61])
	draw_geometries([pcd , mesh_frame])
	#custom_draw_geometry_with_key_callback(pcd)

if __name__ == "__main__":
	file_las = ('nube_convocatoria.las')
	las_file = open(file_las,'rb')
	las_size = os.path.getsize(file_las)
	mapa_las = mmap.mmap(las_file.fileno(),las_size, access=mmap.ACCESS_READ)
	las_values = read_packets_las(414912,mapa_las) #se solicitan los datos del packet 0 del archivo de nube de puntos
	print(las_values)
	print("-------numero de puntos en el las---------------------")
	print(num_datagrams(mapa_las,28,227))

	matrix= points_matrix()
	dibujar(matrix)
