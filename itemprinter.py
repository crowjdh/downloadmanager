import os
import curses
import locale
import strutil

debug = False

# TODO: Change first line of log to show progress
# TODO: Consider adding download speed per item

PORTION_PROGRESS = .8
LENGTH_TITLE = 15
LENGTH_PROGRESS_TEXT = 15
LENGTH_STATUS = 15
LENGTH_PERCENTAGE = 4
ELLIPSIS = '...'

class ItemPrinter:
	def __init__(self, encoding = "utf-8", message = ""):
		rows, cols = os.popen('stty size', 'r').read().split()
		self.termianlRowCnt = int(rows)
		self.termianlColCnt = int(cols)
		self.printRowPadding = int(self.termianlRowCnt * 0.8)
		self.encoding = encoding
		self.message = message

	def setup(self):
		self.cursorIdx = 0

		if debug:
			return

		locale.setlocale(locale.LC_ALL, '')
		global stdscr
		stdscr = curses.initscr()
		curses.noecho()
		curses.cbreak()

	def cleanup(self):
		if debug:
			return

		curses.nocbreak()
		curses.echo()
		curses.endwin()

	def setMessage(self, message):
		self.message = message

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
		
		for itemIdx in printRange:
			printIdx = itemIdx - self.cursorIdx + 1
			self.printItemProgress(items, itemIdx, printIdx, itemsCntDigit)

		self.doPrint()

	def printProgressSummary(self, items):
		doneCount = 0

		for item in items:
			if item.isDone:
				doneCount += 1

		self.printIt(0, 0, "Progress: {0}/{1}\t\t{2}".format(doneCount, len(items), self.message))

	def printItemProgress(self, items, itemIdx, printIdx, itemsCntLength):
		msg = self.buildItemProgressMessage(items, itemIdx, printIdx, itemsCntLength)
		self.printIt(printIdx, 0, msg)

	def buildItemProgressMessage(self, items, itemIdx, printIdx, itemsCntLength):
		msgFormat = "[{itemIdx:>{itemsCntLength}}]{0:>{targetTitleLength}}: [{2:{targetProgressLength}}] {1:>{percentageLength}}%  {3:>{targetStatusLength}} {4:>{targetTextProgressLength}}"
		additionalLength = len(strutil.removeBetween(msgFormat, '{', '}'))

		item = items[itemIdx]
		colsLeft = self.termianlColCnt - LENGTH_STATUS - itemsCntLength - LENGTH_PERCENTAGE - LENGTH_TITLE - LENGTH_PROGRESS_TEXT - additionalLength - 1
		targetTitleLength = LENGTH_TITLE
		targetProgressLength = int(colsLeft * PORTION_PROGRESS)
			
		title = item.title
		if title is not None:
			title = title if type(title) == 'unicode' else title.decode(self.encoding)
			titleLength = len(title)
			if titleLength > targetTitleLength:
				fractionLength = int((targetTitleLength - len(ELLIPSIS)) / 2.)
				title = title[0:fractionLength] + ELLIPSIS + title[titleLength - fractionLength:titleLength]
			title = title.encode(self.encoding)

		progressInPercentage = item.progressInPercentage()
		megabyte = 1024. * 1024.

		progressInBytes = item.getProgress()
		totalSizeInBytes = item.getSize()
		if progressInBytes >= 0 and totalSizeInBytes > 0:
			progressMB = item.getProgress() / megabyte
			totalSizeMB = item.getSize() / megabyte
			progressText = "{0:.2f}MB/{1:.2f}MB".format(progressMB, totalSizeMB)
		else:
			progressText = "0/0"

		return msgFormat.format(
			title, int(progressInPercentage * 100), "#" * int(progressInPercentage*targetProgressLength), item.statusMessage, progressText,
			itemIdx = itemIdx, itemsCntLength = itemsCntLength,
			targetTitleLength = targetTitleLength, targetProgressLength = targetProgressLength,
			targetStatusLength = LENGTH_STATUS, percentageLength = LENGTH_PERCENTAGE,
			targetTextProgressLength = LENGTH_PROGRESS_TEXT)

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
			self.cursorIdx = min(itemCount - self.printRowPadding, self.cursorIdx + 1)
