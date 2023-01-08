import datetime
import praw

from preprocessing.reddit_scrape import reddit_instance

reddit = reddit_instance.get_reddit_instance()

subreddit = reddit.subreddit('python')

# Set the "before" and "after" parameters to the ID of the last post that you retrieved.
before = "105uf6l"  # Replace with the ID of the last post you retrieved.
after = None

# Set a flag to indicate whether there are more posts to retrieve.
more_posts = True

while more_posts:
    # Retrieve the next batch of posts.
    submissions = subreddit.new(limit=100, before=before, after=after)

    # Iterate through the posts and do something with them.
    for submission in submissions:
        print(submission.title)

        # Update the "before" parameter for the next iteration.
        before = submission.id

    # Check if there are more posts to retrieve.
    if submissions.before is None:
        more_posts = False







