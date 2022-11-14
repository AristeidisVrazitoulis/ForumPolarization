'''
Extracting data with the most frequent users
'''
# 
import json
from treelib import Tree


class Extractor:

    def __init__(self, reddit, all_ids=None):
        self.user_counter = {}
        self.user_tracker = {}
        self.all_ids = all_ids
        self.reddit = reddit

        self.counter = 0

    def update_user_counter(self, author_name):
        if author_name not in self.user_counter:
            self.user_counter[author_name] = 1
        else:
            self.user_counter[author_name] += 1

    def traverse_submission(self, submission_id):
        submission = self.reddit.submission(submission_id)
        submission.comments.replace_more(limit=4)
        
        print(self.counter)
        self.counter += 1

        tree = Tree()
        # root node
        tree.create_node(str(submission.author), str(submission.id), data={"score":submission.score,"body":submission.selftext})
        
        self.user_tracker[submission_id] = set() 
        for comment in submission.comments.list():
            comment_author = str(comment.author)
            author_name = comment_author+str(comment.id) if comment_author == "None" else comment_author

            if not(comment.author is None or author_name == "AutoModerator"):
                self.update_user_counter(author_name)
                self.user_tracker[submission_id].add(author_name)

            tree.create_node(
                author_name,
                str(comment.id), 
                parent=str(comment.parent_id[3:]),
                data = {"body":comment.body, "score":comment.score}
            )
        return tree


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
            for id in self.all_ids:
                # submission_ids = submission_ids.union(set(self.user_tracker[user]))
                if user in self.user_tracker[id]:
                    submission_ids.add(id)
    
        return submission_ids

    def eliminate_trees(self, trees, submission_ids):
        new_tree_set = set()
        for tree in trees:
            if tree.root in submission_ids:
                new_tree_set.add(tree)
        
        print("OLD", len(trees))
        print("NEW", len(new_tree_set))
        return new_tree_set

    # returns a list of Treelib objects
    def create_trees(self, ids):
        trees = set()
        # first we make all the trees
        for id in ids:
            tree = self.traverse_submission(id)
            trees.add(tree)
        top_users = self.extract_most_frequent_users(20)
        submission_ids = self.get_submissions_by_top_users(top_users)
        # just for debugging reasons
        self.top_submissions = submission_ids
        # then we make eliminate the trees with low participation
        return self.eliminate_trees(trees, submission_ids)


    def load_data(self, filename):
        folder = r"extract_data/"
        path_name = folder+filename+".json"
        with open(path_name, "r") as f:
            data = json.load(f)
            self.user_counter = data['user_counter']
            self.user_tracker = data['user_tracker']
            self.all_ids = data['all_ids']
            self.top_submissions = data['top_submissions']
        return data


    def save_data_todisk(self, json_data, filename):
        folder = r"extract_data/"
        path_name = folder+filename+".json"
        with open(path_name,"w") as f:
            json.dump(json_data, f)
    

    def gather_data(self, subreddit_name): 
        # convert user tracker values to list
        d = {key:list(value) for (key,value) in self.user_tracker.items()}
        all_data = {
            "all_ids":list(self.all_ids), 
            "user_counter":self.user_counter, 
            "user_tracker":d, 
            "top_submissions": list(self.top_submissions) 
        }
        self.save_data_todisk(all_data, subreddit_name)


    def test_method1(self, subreddit):
        self.all_ids = reddit_parser.extract_top_submissions(subreddit, 20)

        for id in self.all_ids:
            self.traverse_submission(id)

        top_users = self.extract_most_frequent_users(2)
        submission_ids = self.get_submissions_by_top_users(top_users)
        print(len(self.all_ids))
        print(len(submission_ids))
        # just for debugging reasons
        self.top_submissions = submission_ids
    


    def test_method2(self, subreddit):
        self.load_data(subreddit)
        top_users = self.extract_most_frequent_users(1)
        submission_ids = self.get_submissions_by_top_users(top_users)
        print(len(self.all_ids))
        print(len(submission_ids))
        # just for debugging reasons
        self.top_submissions = submission_ids

    def test_method3(self, subreddit):
        # from utils import get_filenames
        self.load_data(subreddit)
        top_users = self.extract_most_frequent_users(20)
        for user in top_users:
            # s = praw.models.Redditor(self.reddit, user)
            for comment in self.reddit.redditor(user).comments.controversial():

                if comment.subreddit == subreddit: 
                    if comment.id not in self.top_submissions:
                        print("new")
                    else:
                        print("exists")

        

if __name__ == "__main__":
    from reddit_parser import RedditParser

    credentials = 'client_secrets.json'
    reddit_parser = RedditParser(credentials)
    reddit = reddit_parser.reddit
    save_data = False
    choice = 's'
    if choice == 'y':
        save_data = True

    subreddit_name = "Coronavirus"
    
    extractor = Extractor(reddit)
    
    extractor.test_method3(subreddit_name)
    
    if save_data:
        extractor.gather_data(subreddit_name)

