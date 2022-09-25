'''
Google's API Perspective
In this file we use the API to measure how 'bad' a comment is
'''

from googleapiclient import discovery


class PerspectiveAPI:
    # TODO hide API_KEY after making the repo public
    __API_KEY = 'AIzaSyAjh9Chd7A8-Nkyz9tK2eWn9p-hbQQmgpc'

    def __init__(self):
        # settings
        # All attributes except SEVERE_TOXICITY
        self.attribute_names = ["TOXICITY","IDENTITY_ATTACK","INSULT","PROFANITY","THREAT"]
        # threshold of insult
        self.threshold = 0.7

        self.client = discovery.build(
            "commentanalyzer",
            "v1alpha1",
            developerKey = PerspectiveAPI.__API_KEY,
            discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
            static_discovery=False,
        )
    
    def __get_attributes_dict(self):
        requested_attr = {}
        for name in self.attribute_names:
            requested_attr[name] = {"scoreThreshold":self.threshold}
        return requested_attr



    def get_scores(self, comment_text):
        analyze_request = {
            'comment': { 'text': comment_text},
            'requestedAttributes': self.__get_attributes_dict()
        }
        response = self.client.comments().analyze(body=analyze_request).execute()
        return response

    def is_prob_insult(self, comment_text):
        return "attributeScores" in self.get_scores(comment_text)



if __name__ == "__main__":
    perspective = PerspectiveAPI()
    response = perspective.is_prob_insult("You're just another brain-dead Muslim here")
    print(response)












