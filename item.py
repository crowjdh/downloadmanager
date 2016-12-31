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

	def setSizeOfItemAt(self, idx, size):
		self.items[idx].setSize(size)

	def setItemSleepingAt(self, idx, sleeping):
		self.items[idx].setSleeping(sleeping)

class Item:
	def __init__(self, url, size = -1, title = None):
		self.url = url
		self.size = size
		self.title = title
		self.progress = 0
		self.isDone = False
		self.sleeping = True

	def getSize(self):
		return self.size

	def setSize(self, size):
		self.size = size

	def setSleeping(self, sleeping):
		self.sleeping = sleeping

	def progressInPercentage(self):
		return 0 if self.size < 0 else self.progress / self.size

	def progressBy(self, progress):
		self.progress += progress
		self.isDone = self.progress >= self.size
