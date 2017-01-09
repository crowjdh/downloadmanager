# Batch Downloader
Batch downloader for Python CLI

# Preview
![preview](/images/preview_01.png)

# Dependencies
See [requirements.txt](https://github.com/crowjdh/downloadmanager/blob/master/requirements.txt)

# Usage
```Python
from downloadmanager import downloader

if __name__ == "__main__":
	fileOne = "https://upload.wikimedia.org/wikipedia/commons/7/74/Earth_poster_large.jpg"
	fileTwo = "http://www.kenrockwell.com/nikon/d600/sample-images/600_0985.JPG"
	fileThree = "http://istg.rootsweb.com/maps/images/lgRRmap.jpg"
  
	itemsArr = [Item(fileOne), Item(fileTwo, title = "SampleImage"), Item(fileThree)]

	with requests.session() as sess:
		downloader.batchDownload(itemsArr, "output", sess = sess)
```
