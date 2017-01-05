import os
import multiprocessing
import time
import signal
from multiprocessing.managers import BaseManager
import curses

import requests
from requests import Session
from readchar import readchar

from item import Item, Items
from itemprinter import ItemPrinter
from loggingpool import LoggingPool

# TODO: Add requirements.txt

class DownloadItemManager(BaseManager): pass

def Manager():
    m = DownloadItemManager()
    m.start()
    return m

DownloadItemManager.register('Items', Items)
DownloadItemManager.register('Session', Session)
DownloadItemManager.register('ItemPrinter', ItemPrinter)

def initPool(l, sessArg, beforeRequestArg, printerArg):
	global lock
	global sess
	global beforeRequest
	global printer
	lock = l
	sess = sessArg
	beforeRequest = beforeRequestArg
	printer = printerArg

def download(arg):
	idx = arg[0]
	outputPath = arg[1]
	items = arg[2]
	with lock:
		waitForAWhile(5, lambda : printer.printProgress(items.getItems()))
		items.setItemsetStatusMessageAt(idx, "Fetching...")
		printer.printProgress(items.getItems())
		if beforeRequest is not None:
			beforeRequest(idx)
		response = sess.get(items.getItem(idx).url, stream=True)
	refactorItem(response, items, idx)

	fileName = addExtensionToFIleName(response, items.getItem(idx).title)
	createDirectory(outputPath)
	filePath = os.path.join(outputPath, fileName)

	items.setItemsetStatusMessageAt(idx, "Downloading...")
	with open(filePath, "wb") as handle:
		for data in response.iter_content(chunk_size=1024):
			handle.write(data)
			with lock:
				items.progressItemBy(idx, len(data))
				printer.printProgress(items.getItems())
	items.setItemsetStatusMessageAt(idx, "Done")
	printer.printProgress(items.getItems())

def waitForAWhile(secs, action):
	resolution = 10
	for i in range(secs * resolution):
		action()
		time.sleep(1. / resolution)

def refactorItem(response, items, idx):
	total_length = int(response.headers.get('Content-Length', 0))

	items.setSizeOfItemAt(idx, total_length)
	itemTitle = items.getItem(idx).title
	if itemTitle is None:
		itemTitle = "Untitled-{0}".format(idx)
		items.setItemTitle(idx, itemTitle)

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

def watchKeyInputUntilDone(items):
	global jobDone
	itemCount = len(items.getItems())
	while not jobDone:
		key = readchar()
		if key == "w":
			printer.moveCursor(itemCount, -1)
		elif key == "s":
			printer.moveCursor(itemCount, 1)
		elif key == '\x1b':
			raise Exception("esc")
		time.sleep(0.1)

def callback(arg):
	global jobDone
	jobDone = True

def exceptionHandler(e, *args, **kwargs):
	args = args[0]
	idx = args[0]
	items = args[2]
	items.setItemsetStatusMessageAt(idx, "Error")
	printer.printProgress(items.getItems())

	if isinstance(e, KeyboardInterrupt):
		raise Exception("KeyboardInterrupt")

def batchDownload(itemsArr, outputPath, sess = requests.session(), beforeRequest = None, processes = 2, printEncoding = 'utf-8'):
	manager = Manager()

	global printer
	printer = manager.ItemPrinter(message = "W: Up, S: Down, ESC: Exit", encoding = printEncoding)
	printer.setup()

	items = manager.Items(itemsArr)

	global jobDone
	jobDone = False

	l = multiprocessing.Lock()

	pool = LoggingPool(initializer = initPool, initargs=(l, sess, beforeRequest, printer), processes = processes, exceptionHandler = exceptionHandler)

	pool.map_async(download, [(idx, outputPath, items) for idx in range(len(itemsArr))], callback = callback)
	try:
		watchKeyInputUntilDone(items)
	except (KeyboardInterrupt, Exception):
		# Cancel gracefully
		pool.terminate()
	else:
		pool.close()
	finally:
		pool.join()
		printer.setMessage("Press any key to exit")
		printer.printProgress(items.getItems())
		readchar()
		printer.cleanup()

if __name__ == "__main__":
	url_5mb = "http://download.thinkbroadband.com/5MB.zip"
	url_10mb = "http://download.thinkbroadband.com/10MB.zip"
	url_20mb = "http://download.thinkbroadband.com/20MB.zip"
	itemsArr = [Item(url_5mb, title = "test title"), Item(url_5mb, title = "test title2"), Item(url_5mb, title = "test title3")]

	with requests.session() as sess:
		batchDownload(itemsArr, "output", sess)
