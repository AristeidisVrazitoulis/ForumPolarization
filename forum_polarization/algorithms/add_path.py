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
p = Path(__file__).parents[1]

p1 = str(p)
sys.path.insert(0, p1)
p2 = p.joinpath("preprocessing")

p3 = Path(__file__).parents[2]

sys.path.insert(1, str(p2))