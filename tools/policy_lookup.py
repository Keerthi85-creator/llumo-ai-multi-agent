class PolicyLookup:
    def __init__(self, passages):
        self.kb = passages
    def lookup(self, query):
        # simple case-insensitive title search
        results = []
        q = query.lower()
        for p in self.kb:
            if p['title'].lower().startswith("company policy") or 'working hours' in p['title'].lower():
                if any(tok in q