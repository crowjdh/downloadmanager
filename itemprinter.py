import curses

debug = False

def setup():
	if debug:
		return

	global stdscr
	stdscr = curses.initscr()
	curses.noecho()
	curses.cbreak()

def cleanup():
	if debug:
		return

	curses.nocbreak()
	curses.echo()
	curses.endwin()

def printProgress(items):
	preparePrint()
	printProgressSummary(items)
	itemsCnt = len(str(len(items)))
	for idx, item in enumerate(items):
		printItemProgress(idx, item, itemsCnt)

	doPrint()

def printProgressSummary(items):
	doneCount = 0

	message = ""
	for item in items:
		if item.isDone:
			message = message + "True\t"
			doneCount += 1
		else:
			message = message + "False\t"
	
	printIt(0, 0, str(doneCount) + "\t" + message)

def printItemProgress(idx, item, itemsCnt):
	progress = item.progressInPercentage()
	msg = "Item {0:>{itemsCnt}}: [{2:50}] {1}%".format(idx, int(progress * 100), "#" * int(progress*50), itemsCnt = itemsCnt)
	printIt(idx+1, 0, msg)

def preparePrint():
	if debug:
		return
	stdscr.clear()

def doPrint():
	if debug:
		return
	stdscr.refresh()

def printIt(y, x, msg):
	if debug:
		print msg
		return
	stdscr.move(y, x)
	stdscr.deleteln()
	stdscr.addstr(y, x, msg)
