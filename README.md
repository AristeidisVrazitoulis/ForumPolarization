# ForumPolarization

Diploma Thesis 

We study various forms of polarization on reddit.

**Unsigned Polarization**: The formation of two disjoint groups with low interaction between them

**Signed Polarization**: The formation of two disjoint subgroups, where the users agree mostly with the users of the same group and disagree with the users belonging to the other group

**Intra-polarization**: examines the formation of polarized groups discussing a specific topic within a single community (subreddit)
**Inter-polarization**: examines the formation of polarized groups discussing a specific topic across two communities (subreddits)


- We collect data using the python module PRAW

- We make a comnment tree for each post we collected

- Out of the trees we make the user conversation graphs

- On the graphs we perform algorithms to measure polarity statistically


For unsigned polarity we use the Random-Walk Algorithm
For signed polarity we use the Random-Eigensign Algorithm


Polarization between lgbt and Conservative communities

![lgbt_conservative](https://user-images.githubusercontent.com/45623442/222721176-98de514e-579a-4343-aa13-2901fc311c4f.png)

We distinguish that there is very low interaction between the communities indicating the lower levels of polarity
