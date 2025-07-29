import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

def count_overlapping_words(sentence1, sentence2):
    # Convert sentences to sets of words
    words1 = set(sentence1.lower().split())
    words2 = set(sentence2.lower().split())

    # Find the intersection of the two sets
    overlapping_words = words1.intersection(words2)

    # Return the count of overlapping words
    return len(overlapping_words)