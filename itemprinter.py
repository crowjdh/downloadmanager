import os
import curses

debug = False

# TODO: Fix error when printing taller then the terminal window
# TODO: Change first line of log to show progress
# TODO: Consider adding download speed per item

class ItemPrinter:
	def __init__(self):
		self.termianlRowCnt = int(os.popen('stty size', 'r').read().split()[0])
		self.printPadding = int(self.termianlRowCnt * 0.8)

	def setup(self):
		if debug:
			return

		global stdscr
		stdscr = curses.initscr()
		curses.noecho()
		curses.cbreak()

		self.cursorIdx = 0

	def cleanup(self):
		if debug:
			return

		curses.nocbreak()
		curses.echo()
		curses.endwin()

	def printProgress(self, items):
		self.preparePrint()
		self.printProgressSummary(items)
		itemsCnt = len(items)
		itemsCntDigit = len(str(itemsCnt))
		printRange = None
		if itemsCnt <= self.termianlRowCnt - 1:
			printRange = range(0, itemsCnt)
		else:
			printRange = range(self.cursorIdx, min(self.cursorIdx + self.termianlRowCnt - 1, itemsCnt))
		self.printIt(0, 0, "printRange: {0}\tcursorIdx: {1}\t".format(printRange, self.cursorIdx))
		
		for itemIdx in printRange:
			printIdx = itemIdx - self.cursorIdx + 1
			self.printItemProgress(items, itemIdx, printIdx, itemsCntDigit)

		self.doPrint()

	def printProgressSummary(self, items):
		doneCount = 0

		message = ""
		for item in items:
			if item.isDone:
				message = message + "True\t"
				doneCount += 1
			else:
				message = message + "False\t"
		
		self.printIt(0, 0, str(doneCount) + "\t" + message)

	def printItemProgress(self, items, itemIdx, printIdx, itemsCnt):
		item = items[itemIdx]
		progress = item.progressInPercentage()
		msg = "Item {0:>{itemsCnt}}: [{2:50}] {1}%\t{sleeping}".format(itemIdx, int(progress * 100), "#" * int(progress*50), itemsCnt = itemsCnt, sleeping="Sleeping" if item.sleeping else "Awake")
		self.printIt(printIdx, 0, msg)

	def preparePrint(self):
		if debug:
			return
		stdscr.clear()

	def doPrint(self):
		if debug:
			return
		stdscr.refresh()

	def printIt(self, y, x, msg):
		if debug:
			return
		stdscr.move(y, x)
		stdscr.deleteln()
		stdscr.addstr(y, x, msg)

	def moveCursor(self, itemCount, direction):
		if direction < 0:
			self.cursorIdx = max(0, self.cursorIdx - 1)
		elif direction > 0:
			# Show few lines more for readability
			self.cursorIdx = min(itemCount - self.printPadding, self.cursorIdx + 1)
		# elif key == '\x1b':
		# 	pass
