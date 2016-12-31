import os
import multiprocessing
import time
import signal
from multiprocessing.managers import BaseManager
import curses

import requests
from requests import Session

from item import Item, Items
import itemprinter

class DownloadItemManager(BaseManager): pass

def Manager():
    m = DownloadItemManager()
    m.start()
    return m

DownloadItemManager.register('Items', Items)
DownloadItemManager.register('Session', Session)

def initPool(l, sessArg, beforeRequestArg):
	global lock
	global sess
	global beforeRequest
	lock = l
	sess = sessArg
	beforeRequest = beforeRequestArg

def download(arg):
	idx = arg[0]
	outputPath = arg[1]
	items = arg[2]
	lock.acquire()
	print "sleep before request: " + str(idx)
	time.sleep(5)
	if beforeRequest is not None:
		beforeRequest(idx)
	response = sess.get(items.getItem(idx).url, stream=True)
	lock.release()

	total_length = int(response.headers.get('Content-Length', 0))

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
	extension = None
	try:
		extension = guess_extension(contentType)
	except:
		extension = None

	if extension is None:
		extensionCandidates = contentType.split("/")
		if len(extensionCandidates) > 1:
			extension = "." + extensionCandidates[1]
		else:
			extension = ".unknown"
	
	return title + extension

def createDirectory(outputPath):
	if not os.path.exists(outputPath):
		os.makedirs(outputPath)

def test():
	print "aaa"

def batchDownload(itemsArr, outputPath, sess = requests.session(), beforeRequest = None):
	itemprinter.setup()

	manager = Manager()
	items = manager.Items(itemsArr)

	l = multiprocessing.Lock()
	pool = multiprocessing.Pool(initializer = initPool, initargs=(l, sess, beforeRequest), processes=2)
	pool.map_async(download, [(idx, outputPath, items) for idx in range(len(itemsArr))])
	pool.close()
	pool.join()

	time.sleep(5)

	itemprinter.cleanup()

if __name__ == "__main__":
	url_5mb = "http://download.thinkbroadband.com/5MB.zip"
	url_10mb = "http://download.thinkbroadband.com/10MB.zip"
	url_20mb = "http://download.thinkbroadband.com/20MB.zip"
	itemsArr = [Item(url_5mb, title = "test title"), Item(url_5mb, title = "test title2"), Item(url_5mb, title = "test title3")]

	with requests.session() as sess:
		batchDownload(itemsArr, "output", sess)
