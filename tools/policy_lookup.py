# tools/policy_lookup.py
class PolicyLookup:
    def __init__(self, passages):
        self.kb = passages

    def lookup(self, query):
        keywords = ['working hours', 'overtime', 'reimburse', 'reimbursements', 'reimbursement']
        q = query.lower()
        hit_keywords = [kw for kw in keywords if kw in q]
        if not hit_keywords:
            return []

        def score_doc(p):
            text = (p.get('title','') + ' ' + p.get('text','')).lower()
            s = 0
            for kw in hit_keywords:
                s += text.count(kw)
            # boost when keyword appears in title
            if any(kw in p.get('title','').lower() for kw in hit_keywords):
                s += 2
            return s

        scored = []
        for p in self.kb:
            s = score_doc(p)
            if s > 0:
                scored.append((s, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored]
