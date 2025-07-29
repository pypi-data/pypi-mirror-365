import numpy as np
import nltk
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

def get_word_embeddings(sentence, model, tokenizer):
    inputs = tokenizer(sentence, return_tensors='pt', truncation=True, padding=True)
    outputs = model(**inputs)
    word_embeddings = outputs.last_hidden_state.squeeze(0)
    tokens = tokenizer.tokenize(sentence)
    return tokens, word_embeddings

def align_words(tokens1, tokens2):
    aligned_pairs = []
    for i, token1 in enumerate(tokens1):
        max_sim = 0
        best_match = None
        for j, token2 in enumerate(tokens2):
            if token1 == token2:
                aligned_pairs.append((i, j))
                break
            else:
                sim = jaccard_similarity(token1, token2)
                if sim > max_sim:
                    max_sim = sim
                    best_match = (i, j)
        if best_match:
            aligned_pairs.append(best_match)
    return aligned_pairs

# Tokenization and lowercasing
def preprocess_text(text):
    return nltk.word_tokenize(text.lower())

# Jaccard Similarity
def jaccard_similarity(str1, str2):
    a = set(preprocess_text(str1))
    b = set(preprocess_text(str2))
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))

# Sentence Embedding Cosine Similarity
def sentence_embedding_cosine_similarity(sent1, sent2, model, tokenizer):
    inputs1 = tokenizer(sent1, return_tensors='pt', truncation=True, padding=True)
    inputs2 = tokenizer(sent2, return_tensors='pt', truncation=True, padding=True)

    with torch.no_grad():
        embeddings1 = model(**inputs1).last_hidden_state.mean(dim=1)
        embeddings2 = model(**inputs2).last_hidden_state.mean(dim=1)

    return cosine_similarity(embeddings1, embeddings2)[0][0]

def contextualized_word_embedding_similarity(sentence1, sentence2, model, tokenizer):
    tokens1, embeddings1 = get_word_embeddings(sentence1, model, tokenizer)
    tokens2, embeddings2 = get_word_embeddings(sentence2, model, tokenizer)
    # print(type(embeddings1))
    aligned_pairs = align_words(tokens1, tokens2)

    if not aligned_pairs:
        return 0  # No aligned words

    similarities = []
    for i, j in aligned_pairs:
        sim = cosine_similarity(embeddings1[i].detach().unsqueeze(0), embeddings2[j].detach().unsqueeze(0))[0][0]
        similarities.append(sim)

    return np.max(similarities) if similarities else 0

# Main function to calculate combined similarity
def combined_similarity(sentence1, sentence2, model, tokenizer, alpha=0.15, gamma=0.30, delta=0.55):
    jaccard_sim = jaccard_similarity(sentence1, sentence2)
    sentence_embedding_sim = sentence_embedding_cosine_similarity(sentence1, sentence2, model, tokenizer)
    contextualized_word_embedding_sim = contextualized_word_embedding_similarity(sentence1, sentence2, model, tokenizer)
    # print(jaccard_sim, sentence_embedding_sim, contextualized_word_embedding_sim)
    return (alpha * jaccard_sim + gamma * contextualized_word_embedding_sim + delta * sentence_embedding_sim)