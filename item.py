from __future__ import division

class Items:
	def __init__(self, items):
		self.items = items

	def getItem(self, idx):
		return self.items[idx]

	def getItems(self):
		return self.items

	def progressItemBy(self, idx, progress):
		self.items[idx].progressBy(progress)

class Item:
	def __init__(self, size):
		self.size = size
		self.progress = 0
		self.isDone = False

	def getSize(self):
		return self.size

	def getIsDone(self):
		return self.isDone

	def progressInPercentage(self):
		return self.progress / self.size

	def getProgress(self):
		return self.progress

	def progressBy(self, progress):
		self.progress += progress
		self.isDone = self.progress >= self.size
