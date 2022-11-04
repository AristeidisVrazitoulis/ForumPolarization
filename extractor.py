'''
Extracting data with the most frequent users
'''
from reddit_parser import RedditParser
import json


class Extractor:

    def __init__(self):
        self.user_counter = {}
        self.user_tracker = {}

    def update_user_counter(self, author_name):
        if author_name not in self.user_counter:
            self.user_counter[author_name] = 1
        else:
            self.user_counter[author_name] += 1

    def update_user_tracker(self, author_name, submission_id):
        if author_name not in self.user_tracker:
            self.user_tracker[author_name] = set()
            self.user_tracker[author_name].add(submission_id)
        else:
            if not submission_id in self.user_tracker[author_name]:
                self.user_tracker[author_name].add(submission_id)

    def traverse_submission(self, submission_id):
        submission = reddit.submission(submission_id)
        submission.comments.replace_more(limit=8)

        for comment in submission.comments.list():
            if comment.author is None:
                continue
            author_name = str(comment.author)
            self.update_user_counter(author_name)
            self.update_user_tracker(author_name, submission_id)

    def save_data_todisk(self, json_data, filename):
        folder = r"extract_data/"
        path_name = folder+filename+".json"
        with open(path_name,"w") as f:
            json.dump(json_data, f)
    
    def gather_data(self): 
        # convert user tracker values to list
        d = {key:list(value) for (key,value) in self.user_tracker.items()}
        all_data = {"all_ids":top_ids, "user_counter":self.user_counter, "user_tracker":d}
        self.save_data_todisk(all_data, subreddit_name)


    def extract_most_frequent_users(self, k):
        # users with the largest frequency of posting comments
        top_users = []
        sort_users = {k: v for k, v in reversed(sorted(self.user_counter.items(), key=lambda item: item[1]))}

        for i,user in enumerate(sort_users):
            top_users.append(user)
            if i == k-1:
                break
        
        return top_users

    def get_submissions_by_top_users(self, top_users):
        submission_ids = set()
        for user in top_users:
            # here happens the magic
            submission_ids = submission_ids.union(set(self.user_tracker[user]))

        return submission_ids

        


credentials = 'client_secrets.json'
reddit_parser = RedditParser(credentials)
reddit = reddit_parser.reddit


subreddit_name = "conspiracy"
subreddit = reddit.subreddit(subreddit_name)

top_ids = reddit_parser.extract_top_submissions(subreddit, 1)
extractor = Extractor()

for id in top_ids:
    extractor.traverse_submission(id)

print(extractor.user_tracker)


top_users = extractor.extract_most_frequent_users(5)
print(top_users)
sub_ids = extractor.get_submissions_by_top_users(top_users)
print(sub_ids)



# print(user_counter)
# print(user_tracker)

