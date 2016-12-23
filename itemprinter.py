import curses

def setup():
	global stdscr
	stdscr = curses.initscr()
	curses.noecho()
	curses.cbreak()

def cleanup():
	curses.nocbreak()
	curses.echo()
	curses.endwin()

def printProgress(items):
	stdscr.clear()
	printProgressSummary(items)
	itemsCnt = len(str(len(items)))
	for idx, item in enumerate(items):
		printItemProgress(idx, item, itemsCnt)

	stdscr.refresh()

def printProgressSummary(items):
	doneCount = 0

	message = ""
	for item in items:
		if item.isDone:
			message = message + "True\t"
			doneCount += 1
		else:
			message = message + "False\t"
	
	stdscr.move(0, 0)
	stdscr.deleteln()
	stdscr.addstr(0, 0, str(doneCount) + "\t" + message)

	stdscr.refresh()

def printItemProgress(idx, item, itemsCnt):
	progress = item.progressInPercentage()
	msg = "Item {0:>{itemsCnt}}: [{2:50}] {1}%".format(idx, int(progress * 100), "#" * int(progress*50), itemsCnt = itemsCnt)
	stdscr.move(idx+1, 0)
	stdscr.deleteln()
	stdscr.addstr(idx+1, 0, msg)

	stdscr.refresh()
