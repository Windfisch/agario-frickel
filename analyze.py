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
print("\n" + "-"*40 + "\n")
s.analyze_visible_window(False)
for i in ["split cell", "ejected mass", "virus"]:
    s.analyze_deviations(i)
print("")
for i in ["split cell", "ejected mass", "virus"]:
    s.analyze_distances(i)

s.analyze_virus_sizes()
s.analyze_remerge()
