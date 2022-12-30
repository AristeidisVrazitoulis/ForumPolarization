# import sys
# import os
# import inspect

# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# parentdir = os.path.dirname(parentdir)
# print(type(parentdir))
# sys.path.insert(0, parentdir)


from pathlib import Path
import sys
p = Path(__file__).parents[2]
p = str(p)
sys.path.insert(0, p)