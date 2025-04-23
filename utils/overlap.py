import nltk
from rouge_score import rouge_scorer
import json
from evaluate import load
from bert_score import BERTScorer

nltk.download('punkt')

def jaccard_similarity(text1, text2, n=2):
    """Computes Jaccard Similarity between two texts based on n-grams."""
    
    # Tokenize the texts
    tokens1 = set(nltk.word_tokenize(text1.lower()))  # Lowercase for consistency
    tokens2 = set(nltk.word_tokenize(text2.lower()))

    # Compute Jaccard similarity
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2

    return len(intersection) / len(union) if union else 0  # Avoid division by zero


def compute_rouge(text1, text2):
    """Computes ROUGE scores between two texts."""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(text1, text2)
    return scores['rouge1'], scores['rouge2'], scores['rougeL']

def compute_bert(text1,text):
    scorer = BERTScorer(model_type='bert-base-uncased')
    P, R, F1 = scorer.score([text1], [text2])
    return P.mean(), R.mean(), F1.mean()

harm_data = None
safe_data = None

with open("data/harm.json", "r") as f:
    harm_data = json.load(f)

with open("data/safe.json", "r") as f:
    safe_data = json.load(f)


acc_jaccard = 0
acc_rouge_precision = 0
acc_rouge_recall = 0
acc_rouge_f1 = 0

for i in range(0,len(harm_data)):
    text1= harm_data[i]["intent"]
    text2= safe_data[i]["intent"]

    jaccard= jaccard_similarity(text1, text2)
    rouge1, rouge2, rougeL = compute_rouge(text1, text2)

    acc_jaccard += jaccard
    acc_rouge_precision += rougeL.precision
    acc_rouge_recall += rougeL.recall
    acc_rouge_f1 += rougeL.fmeasure



print("Jaccard Similarity: ", acc_jaccard/len(harm_data))
print("ROUGE Precision: ", acc_rouge_precision/len(harm_data))
print("ROUGE Recall: ", acc_rouge_recall/len(harm_data))
print("ROUGE F1: ", acc_rouge_f1/len(harm_data))


