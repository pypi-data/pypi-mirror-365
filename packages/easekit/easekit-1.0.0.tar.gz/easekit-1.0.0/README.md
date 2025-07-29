# EASE Metric

`easekit` is a composite metric to evaluate empathy in dialogue systems. It incorporates:

- **Semantic Relevance**
- **Sentiment Alignment**
- **Contextual Word Overlap**

## Installation

```bash
pip install easekit
```

To use the metric:
```bash
from transformers import AutoTokenizer, AutoModel
from easekit import compute_empathy_score

context = "I am very upset"
response = "Why? Is everything alright?"
reference = "Why? What happened?"

model_name = "sentence-transformers/paraphrase-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

result = compute_empathy_score(context, response, reference, model, tokenizer)
print(result)
