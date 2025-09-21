import json, time, hashlib, re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

from tools.retriever import Retriever, load_kb_from_file
from tools.calculator import safe_eval_expr
from tools.policy_lookup import PolicyLookup
from tools.string_tools import StringTools


# --- Simple in-memory cache ---
class SimpleCache:
    def __init__(self):
        self._d = {}
    def get(self, key): return self._d.get(key)
    def set(self, key, value): self._d[key] = value


# --- Timeout wrapper ---
_executor = ThreadPoolExecutor(max_workers=6)
def run_with_timeout(fn, args=(), timeout=5):
    fut = _executor.submit(fn, *args)
    try:
        return fut.result(timeout=timeout)
    except FutureTimeout:
        fut.cancel()
        raise TimeoutError("timeout")


# --- Agent ---
class Agent:
    def __init__(self, retriever, policy_lookup, cache=None):
        self.retriever = retriever
        self.policy_lookup = policy_lookup
        self.cache = cache or SimpleCache()
        self.logs = []

    def plan(self, query):
        if re.search(r'\d', query) and re.search(r'[%\+\-\*\/]', query):
            return ['calculator']
        if any(word in query.lower() for word in ['policy','working hours','reimbursement']):
            return ['policylookup']
        return ['retriever']

    def run_tool_with_retries(self, tool_name, func, *args, retries=2, timeout=4):
        cache_key = hashlib.sha256((tool_name + '|' + json.dumps(args, default=str)).encode()).hexdigest()
        cached = self.cache.get(cache_key)
        if cached:
            return {'cached': True, 'result': cached, 'meta': {'retries': 0}}
        last_exc = None
        for attempt in range(1, retries+1):
            try:
                start = time.time()
                res = run_with_timeout(func, args=args, timeout=timeout)
                dur = (time.time()-start)*1000
                self.cache.set(cache_key, res)
                return {'cached': False, 'result': res, 'meta': {'retries': attempt-1, 'duration_ms': dur}}
            except Exception as e:
                last_exc = e
                time.sleep(0.2 * attempt)
        raise last_exc

    def handle(self, query):
        run_id = hashlib.sha1(query.encode()).hexdigest()[:8]
        ts = datetime.utcnow().isoformat() + 'Z'
        plan_steps = self.plan(query)
        self.logs.append({'id': run_id, 'timestamp': ts, 'stage': 'plan', 'details': plan_steps})
        final_answer = None
        tool_calls = []

        for step in plan_steps:
            if step == 'calculator':
                def calc_fn(q): return safe_eval_expr(q)
                res = self.run_tool_with_retries('calculator', calc_fn, query)
                tool_calls.append({'tool': 'calculator', 'input': query, 'output': str(res['result'])})
                final_answer = str(res['result'])

            elif step == 'policylookup':
                def pl_fn(q): return self.policy_lookup.lookup(q)
                res = self.run_tool_with_retries('policylookup', pl_fn, query)
                tool_calls.append({'tool': 'policylookup', 'input': query, 'output': [p['title'] for p in res['result']]})
                if res['result']:
                    final_answer = res['result'][0]['text']

            elif step == 'retriever':
                def r_fn(q): return self.retriever.retrieve(q, k=3)
                res = self.run_tool_with_retries('retriever', r_fn, query)
                tool_calls.append({'tool': 'retriever', 'input': query, 'output_count': len(res['result'])})
                if res['result']:
                    final_answer = res['result'][0]['text']

        self.logs.append({'id': run_id, 'stage': 'tool_calls', 'details': tool_calls})
        self.logs.append({'id': run_id, 'stage': 'critic', 'details': {'ok': final_answer is not None}})
        output_record = {'id': run_id, 'timestamp': ts, 'query': query, 'final_output': final_answer}
        self.logs.append({'id': run_id, 'stage': 'final', 'details': output_record})
        return output_record

    def dump_logs(self, path='logs.json'):
        with open(path,'w') as f: json.dump(self.logs, f, indent=2)


if __name__ == '__main__':
    kb = load_kb_from_file('knowledgeBase.txt')
    retr = Retriever(kb)
    pol = PolicyLookup(kb)
    agent = Agent(retr, pol)

    # Test queries (from Test_Queries.pdf)
    queries = [
        #"What is LLUMO AI's core value proposition?",
        #"What does the LLUMO Debugger show that helps isolate failures?",
        "What are the official working hours and overtime rules?",
        #"How do reimbursements work and how long do they take after approval?",
        #"Compute: (125 * 6) - 50 and 15% of 640"
    ]

    for q in queries:
        print(agent.handle(q))
    agent.dump_log