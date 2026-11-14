import sys
import time
from urllib.request import urlopen
for attempt in range(30):
    try:
        print(urlopen(sys.argv[1], timeout=2).read().decode("utf-8"))
        break
    except OSError:
        if attempt == 29:
            raise
        time.sleep(1)
