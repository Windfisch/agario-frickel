from stats import *
import sys

if len(sys.argv) >= 2:
    files = sys.argv[1:]
else:
    files = ["stats.pickle"]


s = Stats.load(files[0])
for f in files[1:]:
    s.merge(f)

s.analyze_speed()
s.analyze_visible_window()

