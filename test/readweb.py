import sys
import os
import json
sys.path.append((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from wfreadable.WFReadable import *

url = sys.argv[1]

try:
    parser = WFReadable(url)
    obj = parser.parse()
    print json.dumps(obj, indent=4)
except PageFetchError:
    print "Fail to fetch web page"
except WebParseError:
    print "Fail to parse web structure"
except WebSummarizeError:
    print "Fail to summarize web content"
