import reddit_instance
import matplotlib.pyplot as plt


plot = True
keyword = "abortion"
reddit = reddit_instance.get_reddit_instance()
sub = reddit.subreddit("all")
d = {}
results = sub.search(keyword, sort="top", limit = None)
s = 0


for result in results:
    s += 1
    subname = str(result.subreddit)
    if subname not in d:
        d[subname] = 1
    else:
        d[subname] += 1
print(s)

d = {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}
print(d)
if plot:
    plot_top = 5
    keys = list(d.keys())
    values = list(d.values())
    keys = keys[:plot_top]
    values = values[:plot_top]
    plt.bar(keys, values)
    plt.tight_layout()
    plt.show()



