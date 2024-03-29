import nltk
import ssl
from nltk.sentiment import SentimentIntensityAnalyzer

# Download NLTK resources (run once)
nltk.download("vader_lexicon")

# Initialize Sentiment Analyzer
sid = SentimentIntensityAnalyzer()

# Example song lyrics
lyrics = """
Put your loving hand out, baby
I'm beggin'
Beggin', beggin' you
Put your loving hand out baby
Beggin', beggin' you
Put your loving hand out darlin'
"""

# Split lyrics into lines
lines = []
for line in lyrics.split("\n"):
    line = line.strip()
    if line:
        lines.append(line)

# Analyze sentiment of each line
mood_per_line = []

for line in lines:
    sentiment_scores = sid.polarity_scores(line)
    if sentiment_scores["compound"] >= 0.10:
        mood = "Positive"
    elif sentiment_scores["compound"] <= -0.10:
        mood = "Negative"
    else:
        mood = "Neutral"
    mood_per_line.append((line, mood))

# Print sentiment analysis for each line
for line, mood in mood_per_line:
    print(f"Line: {line} | Mood: {mood}")
