import multiprocessing
import time
import signal
from multiprocessing.managers import BaseManager
import curses

from item import Item, Items
import itemprinter

class DownloadItemManager(BaseManager): pass

def Manager():
    m = DownloadItemManager()
    m.start()
    return m

DownloadItemManager.register('Items', Items)

def initPool(l):
	def sig_int(signal_num, frame):
		itemprinter.cleanup()
		print 'signal: %s' % signal_num
	signal.signal(signal.SIGINT, sig_int)
	global lock
	lock = l

def download(arg):
	idx = arg[0]
	items = arg[1]
	item = items.getItem(idx)

	for i in range(item.size):
		time.sleep(0.01)
		lock.acquire()
		items.progressItemBy(idx, 1)
		itemprinter.printProgress(items.getItems())
		lock.release()

if __name__ == "__main__":
	itemprinter.setup()

	manager = Manager()

	itemsArr = [Item(10), Item(20), Item(30), Item(40), Item(50), Item(40), Item(30), Item(20), Item(20), Item(20), Item(20)]
	items = manager.Items(itemsArr)

	l = multiprocessing.Lock()
	pool = multiprocessing.Pool(initializer = initPool, initargs=(l,), processes=2)
	result = pool.map_async(download, [(idx, items) for idx in range(len(itemsArr))])

	while True:
		try:
			result.get(0xfff)
		except multiprocessing.TimeoutError as ex:
			pass
	pool.close()
	pool.join()

	time.sleep(5)

	itemprinter.cleanup()
