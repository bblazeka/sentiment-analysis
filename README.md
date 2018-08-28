# sentiment-analysis

In this repository, we examine which algorithms would be best applied for sentiment analysis of reddit posts.

### How the dictionaries were created

LabMT (MANUAL) - language assessment by Mechanical Turk, 50 ratings

Sent140Lex (AUTO) - created from the “sentiment140” corpus of tweets, using Pairwise Mutual Information (measure of association used in information theory and statistics) with emoticons as positive and negative labels

VADER (MANUAL) - "method developed specifically for Twitter and social media analysis", all words were rated by 10 experts and their average was the rating (Mechanical Turk survey, 10 ratings)

HashtagSent (AUTO) - NRC Hashtag Sentiment Lexicon: created from tweets using Pairwise Mutual Information with sentiment hashtags as positive and negative labels

SentiWordNet (AUTO) - WordNet synsets each assigned three sentiment scores: positivity, negativity, and objectivity.

SenticNet (AUTO) - Sentiment dataset labeled with semantics and 5 dimensions of emotions by Cambria et al. (label propagation)

SOCAL (MANUAL) - Manually constructed general-purpose sentiment dictionary

WDAL (MANUAL) - Whissel’s Dictionary of Affective Language: words rated in terms of their Pleasantness, Activation, and Imagery (concreteness) (Survey: Columbia students)

### Running the repository

To run the sentiment analysis, you need to make sure you have all the required datasets and you need to write:
`python3 test.py`

### Resources:

https://github.com/cjhutto/vaderSentiment

https://github.com/andyreagan/labMT-simple