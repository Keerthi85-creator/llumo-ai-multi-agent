import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class Retriever:
    def __init__(self, passages):
        self.passages = passages
        texts = [p['text'] for p in passages]
        self.vec = TfidfVectorizer().fit(texts)
        self.mat = self.vec.transform(texts)

    def retrieve(self, query, k=3):
        qv = self.vec.transform([query])
        scores = (self.mat @ qv.T).toarray()[:,0]
        idx = np.argsort(scores)[::-1][:k]
        return [{'score': float(scores[i]), **self.passages[i]} for i in idx if scores[i] > 0]


def load_kb_from_file(path='knowledgeBase.txt'):
    docs = []
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    parts = text.split('[DOC-')
    for p in parts[1:]:
        header, body = p.split(']', 1)
        id_num = header.strip()
        lines = [l.strip() for l in body.strip().splitlines() if l.strip()]
        title = lines[0].replace('Title:', '').strip() if lines[0].lower().startswith('title:') else f'DOC-{id_num}'
        remaining = ' '.join(lines[1:]).strip()
        if remaining.lower().startswith('text:'):
            remaining = remaining[len('text:'):].strip()
        docs.append({'id': f'DOC-{id_num}', 'title': title, 'text': remaining})
    return docs

