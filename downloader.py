import os
import multiprocessing
import time
import signal
from multiprocessing.managers import BaseManager
import curses

import requests

from item import Item, Items
import itemprinter

class DownloadItemManager(BaseManager): pass

def Manager():
    m = DownloadItemManager()
    m.start()
    return m

DownloadItemManager.register('Items', Items)

def initPool(l):
	global lock
	lock = l

def download(arg):
	idx = arg[0]
	items = arg[1]
	with requests.session() as sess:
		response = sess.get(items.getItem(idx).url, stream=True)
		total_length = int(response.headers.get('Content-Length', 0))
		print "idx: {0}\tsize: {1}".format(idx, total_length)

		items.setSizeOfItemAt(idx, total_length)
		fileName = addExtensionToFIleName(response, items.getItem(idx).title)
		createDirectory(outputPath)
		filePath = os.path.join(outputPath, fileName)

		with open(filePath, "wb") as handle:
			for data in response.iter_content(chunk_size=1024):
				handle.write(data)
				lock.acquire()
				items.progressItemBy(idx, len(data))
				itemprinter.printProgress(items.getItems())
				lock.release()

def addExtensionToFIleName(response, title):
	contentType = response.headers.get('Content-Type')
	extension = guess_extension(contentType)
	if extension is None:
		extensionCandidates = contentType.split("/")
		if len(extensionCandidates) > 1:
			extension = "." + extensionCandidates[1]
		else:
			extension = ".unknown"
	
	return title + extension

def createDirectory(outputPath)
	if not os.path.exists(outputPath):
		os.makedirs(outputPath)

def batchDownload(itemsArr, outputPath):
	itemprinter.setup()

	manager = Manager()
	items = manager.Items(itemsArr)

	l = multiprocessing.Lock()
	pool = multiprocessing.Pool(initializer = initPool, initargs=(l,), processes=2)
	pool.map_async(download, [(idx, items) for idx in range(len(itemsArr))])
	pool.close()
	pool.join()

	time.sleep(5)

	itemprinter.cleanup()

if __name__ == "__main__":
	url_5mb = "http://download.thinkbroadband.com/5MB.zip"
	url_10mb = "http://download.thinkbroadband.com/10MB.zip"
	url_20mb = "http://download.thinkbroadband.com/20MB.zip"
	itemsArr = [Item(url_5mb, title = "test title"), Item(url_5mb, title = "test title2"), Item(url_5mb, title = "test title3")]

	batchDownload(itemsArr, "output")
