import sys
import os
import json
sys.path.append((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from wfreadable.WFReadable import *

url = sys.argv[1]
parser = WFReadable(url)
obj = parser.parse()
print json.dumps(obj, indent=4)
