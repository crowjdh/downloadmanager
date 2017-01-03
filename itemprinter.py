import os
import curses

debug = False

# TODO: Fix error when printing taller then the terminal window
# TODO: Change first line of log to show progress
# TODO: Consider adding download speed per item

def setup():
	if debug:
		return

	global stdscr
	global termianlRowCnt

	stdscr = curses.initscr()
	curses.noecho()
	curses.cbreak()

	termianlRowCnt = int(os.popen('stty size', 'r').read().split()[0])

def cleanup():
	if debug:
		return

	curses.nocbreak()
	curses.echo()
	curses.endwin()

def printProgress(items, cursorIdx = 0):
	preparePrint()
	printProgressSummary(items)
	itemsCnt = len(items)
	itemsCntDigit = len(str(itemsCnt))
	printRange = None
	if itemsCnt <= termianlRowCnt - 1:
		printRange = range(0, itemsCnt)
	else:
		printRange = range(cursorIdx, min(cursorIdx + termianlRowCnt, itemsCnt))
	for idx in printRange:
		item = items[idx]
		printItemProgress(idx, item, itemsCntDigit)

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
	msg = "Item {0:>{itemsCnt}}: [{2:50}] {1}%\t{sleeping}".format(idx, int(progress * 100), "#" * int(progress*50), itemsCnt = itemsCnt, sleeping="Sleeping" if item.sleeping else "Awake")
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
