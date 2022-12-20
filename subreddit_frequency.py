import reddit_instance
import praw

keyword = "patriarchy"
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


