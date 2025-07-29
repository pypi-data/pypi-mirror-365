from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
from transformers import pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

def sentimental_score(input, response):
    vresponse = sentiment_pipeline(response)
    vsresponse = analyzer.polarity_scores(response)
    vinput = sentiment_pipeline(input)
    # vsinput = analyzer.polarity_scores(input)
    neu = vsresponse['neu']
    neg = (vresponse[0]['score'] + vsresponse['neg'])/2
    pos = (vresponse[0]['score'] + vsresponse['pos'])/2
    if vinput[0]['label'] == 'POSITIVE':
      if vresponse[0]['label'] != 'NEGATIVE':
        return max(neu,pos)
      else:
        return -neg
    else:
      if neg>neu:
        if (vinput[0]['score']-neg)>0.5:
          return -(vinput[0]['score']-neg)
        else:
          return -neg
      elif pos>neu:
        if pos<0.5:
          return -(vinput[0]['score']-pos)
        else:
          return -pos
      else:
        return neu