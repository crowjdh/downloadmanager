def removeBetween(msg, startChar, endChar):
	ranges = extractRangeWithDelimeter(msg, startChar, endChar)

	for st, ed in reversed(ranges):
		msg = msg[0:st] + msg[ed+1:len(msg)]

	return msg


def extractRangeWithDelimeter(msg, startChar, endChar):
	stack = []
	ranges = []
	startIdx = -1
	for idx, c in enumerate(msg):
		if c == startChar:
			if startIdx < 0:
				startIdx = idx
			stack.append(c)
		elif c == endChar and startIdx >= 0:
			stack.pop()
			if len(stack) == 0:
				ranges.append((startIdx, idx))
				startIdx = -1
	return ranges
