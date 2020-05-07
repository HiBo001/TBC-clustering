# -*- coding: utf-8 -*-
"""
Created on Thur May 7 10:55:17 2020
@author: Thbobo
"""
#############################################################################
# Full Imports
import os
import csv
import numpy as np
import random
import math
import time
from datetime import datetime

class Center(object):
	def __init__(self, vector):
		self.vector = vector
		self.object = list()
		self.points = map()
		self.clusterBound = 0

class Vector(object):
	def __init__(self, label):
		self.distance_to_clusters = map()
		self.values = list()
		self.label = label

	def addToNearestCenter(self, centers, TBCclusterSize_pool):
		self.distance_to_clusters = {}
		for center in centers:
			distance = self.distance(center.vector)
			self.distance_to_clusters[center] = distance
		sorted_distance_to_clusters_list = list(sorted(self.distance_to_clusters.items(),key = lambda x:x[1],reverse = False))

		i = 0
		while i < len(centers):
			c = sorted_distance_to_clusters_list[i][0]
			if c.clusterBound == 0:
				bound = min(TBCclusterSize_pool)
				c.clusterBound = bound
			else:
				bound = c.clusterBound

			if len(c.object) < bound:
				c.object.append(self)
				c.points[self] = sorted_distance_to_clusters_list[i][1]
				if len(c.object) == min(TBCclusterSize_pool):
					TBCclusterSize_pool.remove(len(c.object))
				return None

			else:
				sorted_c_points_list = list(sorted(c.points.items(),key = lambda x:x[1],reverse = False))
				length = len(sorted_c_points_list)
				farthest_vector = sorted_c_points_list[length-1][0]
				maxdistance = sorted_c_points_list[length-1][1]
				if maxdistance > sorted_distance_to_clusters_list[i][1]:
					c.points.pop(farthest_vector)
					c.object.remove(farthest_vector)
					c.points[self] = sorted_distance_to_clusters_list[i][1]
					c.object.append(self)
					return farthest_vector
			i = i+1

	def distance(self, vector):
		square_sum = 0.0
		a = np.array(self.values)
		b = np.array(vector.values)
		square_sum =  np.sqrt(np.sum(np.square(a - b)))
		return round(square_sum,10)

class TBC(object):
	def __init__(self):
		self.vectors = list()
		self.centers = list()
		self.last_cost = 0.0

	def loadFromFile(self,dir_name):
		for file_name in os.listdir(dir_name):
			csv_reader = csv.reader(open(dir_name+"\\"+file_name,encoding = 'utf-8'))
			n = 0
			for row in csv_reader:
				items = list()
				label = row[0:1]
				v = Vector(label)
				for item in row[0:]:
					items.append(float(item))
				v.values = items
				self.vectors.append(v)

	def start(self,class_num, clusterSize_pool):
		copy_clusterSize_pool = clusterSize_pool.copy()
		original_data = self.vectors.copy()
		for vector in random.sample(original_data,class_num):
			c = Center(vector)
			self.centers.append(c)
			original_data.remove(vector)

		self.split(copy_clusterSize_pool)
		self.locateCenter()
		self.last_cost = self.costFunction()

		i = 2
		while 1:
			copy_clusterSize_pool = clusterSize_pool.copy()
			i += 1
			self.split(copy_clusterSize_pool)
			current_cost = self.costFunction()
			if abs(self.last_cost - current_cost) < 0.001 or i == 100:
				break
			else:
				self.last_cost = current_cost

		dic_of_data = map{}
		for i in range(class_num):
			dic_of_data[self.centers[i].vector] = i
			for j in range(len(self.centers[i].object)):
				dic_of_data[self.centers[i].object[j]] = i

		pre_label = list()
		original_data = self.vectors.copy()
		for v in original_data:
			for d in dic_of_data.keys():
				if d == v:
					pre_label.append(dic_of_data[d])
					break

		distribution = list()
		cs = list()
		for i in self.centers:
			cs.append(i.vector.values)
			distribution.append(len(i.object))
		return pre_label, distribution, current_cost

	def split(self, clusterSize_pool):
		for center in self.centers:
			center.object = list()
			center.points = map()
			center.clusterBound = 0

		for vector in self.vectors:
			farthest_vector = vector.addToNearestCenter(self.centers, clusterSize_pool)
			while farthest_vector != None:
				farthest_vector = farthest_vector.addToNearestCenter(self.centers, clusterSize_pool)

	def locateCenter(self):
		count = 0
		for center in self.centers:
			center.clusterBound = 0
			count += 1.0
			file_count = float(len(center.object))
			new_center = np.array([0.0, 0.0])

			if len(center.object) != 0:
				for vector in center.object:
					new_center += np.array(vector.values)
				new_center = [x/file_count for x in new_center]
				center.vector.values = new_center

	def costFunction(self):
		total_cost = 0.0
		count = 0
		for center in self.centers:
			c_total_cost = 0.0
			count += 1
			for vector in center.object:
				c_total_cost += math.pow(vector.distance(center.vector),2)
			total_cost = total_cost + c_total_cost
		return total_cost

cs = list()
results = list()
pre_labels = list()
ss = 0

N = 5000
tao = 500
K = 15

p = 6
x = int(math.ceil((N-p*tao)/K) + tao)

clusterSize_pool = list()
for i in range(p):
	clusterSize_pool.append(x)
for i in range(K-p):
	clusterSize_pool.append(x-tao)
for i in range(len(clusterSize_pool)):
	if clusterSize_pool[i] < 0:
		clusterSize_pool[i] = 1

for i in range(1):
	km = TBC()
	dir_name = r"... ..."
	km.loadFromFile(dir_name)
	start = datetime.now()
	pre_label, distribution, current_cost = km.start(15, clusterSize_pool.copy())
	end = datetime.now()
	exec_time = end - start
	ss = ss + exec_time.microseconds
	del km
	pre_labels.append(pre_label)
print(pre_labels)
print(ss/1,'ms')