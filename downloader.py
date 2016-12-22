from tqdm import tqdm, trange
import time
import multiprocessing
from multiprocessing.managers import BaseManager
from functools import partial
from item import Item, Items
import curses
import time

class MyManager(BaseManager): pass

def Manager():
    m = MyManager()
    m.start()
    return m

MyManager.register('Items', Items)
MyManager.register('Item', Item)

def initPool(l):
	global lock
	lock = l

def report_progress(items):
	stdscr.clear()
	printProgressSummary(items)
	for idx, item in enumerate(items.getItems()):
		printProgress(idx, item)

	stdscr.refresh()

def printProgressSummary(items):
	doneCount = 0

	message = ""
	for item in items.getItems():
		if item.getIsDone():
			message = message + "True\t"
			doneCount += 1
		else:
			message = message + "False\t"
	
	stdscr.move(0, 0)
	stdscr.deleteln()
	stdscr.addstr(0, 0, str(doneCount) + "\t" + message)

	stdscr.refresh()

def printProgress(idx, item):
	progress = item.progressInPercentage()
	msg = "Item {0}: [{2:51}] {1}%".format(idx, int(progress * 100), "#" * int(progress*50))
	stdscr.move(idx+1, 0)
	stdscr.deleteln()
	stdscr.addstr(idx+1, 0, msg)

	stdscr.refresh()

def download(arg):
	idx = arg[0]
	items = arg[1]
	item = items.getItem(idx)

	for i in range(item.getSize()):
		time.sleep(0.01)
		lock.acquire()
		items.progressItemBy(idx, 1)
		report_progress(items)
		lock.release()

if __name__ == "__main__":
	stdscr = curses.initscr()
	curses.noecho()
	curses.cbreak()

	manager = Manager()

	itemsArr = [manager.Item(10), manager.Item(20), manager.Item(30), manager.Item(40), manager.Item(50), manager.Item(40), manager.Item(30), manager.Item(20), manager.Item(20), manager.Item(20), manager.Item(20)]
	items = manager.Items(itemsArr)

	l = multiprocessing.Lock()
	pool = multiprocessing.Pool(initializer = initPool, initargs=(l,), processes=2)

	pool.map(download, [(idx, items) for idx in range(len(itemsArr))])
	pool.close()
	pool.join()

	report_progress(items)

	time.sleep(5)

	curses.echo()
	curses.nocbreak()
	curses.endwin()
