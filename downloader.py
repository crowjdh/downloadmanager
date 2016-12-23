import multiprocessing
import time
from multiprocessing.managers import BaseManager
import curses

from tqdm import tqdm, trange
from item import Item, Items

class DownloadItemManager(BaseManager): pass

def Manager():
    m = DownloadItemManager()
    m.start()
    return m

DownloadItemManager.register('Items', Items)

def initPool(l):
	global lock
	lock = l

def printProgress(items):
	stdscr.clear()
	printProgressSummary(items)
	for idx, item in enumerate(items.getItems()):
		printItemProgress(idx, item)

	stdscr.refresh()

def printProgressSummary(items):
	doneCount = 0

	message = ""
	for item in items.getItems():
		if item.isDone:
			message = message + "True\t"
			doneCount += 1
		else:
			message = message + "False\t"
	
	stdscr.move(0, 0)
	stdscr.deleteln()
	stdscr.addstr(0, 0, str(doneCount) + "\t" + message)

	stdscr.refresh()

def printItemProgress(idx, item):
	progress = item.progressInPercentage()
	msg = "Item {0}: [{2:50}] {1}%".format(idx, int(progress * 100), "#" * int(progress*50))
	stdscr.move(idx+1, 0)
	stdscr.deleteln()
	stdscr.addstr(idx+1, 0, msg)

	stdscr.refresh()

def download(arg):
	idx = arg[0]
	items = arg[1]
	item = items.getItem(idx)

	for i in range(item.size):
		time.sleep(0.01)
		lock.acquire()
		items.progressItemBy(idx, 1)
		printProgress(items)
		lock.release()

if __name__ == "__main__":
	stdscr = curses.initscr()
	curses.noecho()
	curses.cbreak()

	manager = Manager()

	itemsArr = [Item(10), Item(20), Item(30), Item(40), Item(50), Item(40), Item(30), Item(20), Item(20), Item(20), Item(20)]
	items = manager.Items(itemsArr)

	l = multiprocessing.Lock()
	pool = multiprocessing.Pool(initializer = initPool, initargs=(l,), processes=2)

	pool.map(download, [(idx, items) for idx in range(len(itemsArr))])
	pool.close()
	pool.join()

	time.sleep(5)

	curses.echo()
	curses.nocbreak()
	curses.endwin()
