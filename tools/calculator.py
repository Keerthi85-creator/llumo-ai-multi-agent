import ast
import re

# Allowed operations
ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv)
ALLOWED_UNARYOPS = (ast.UAdd, ast.USub)

def safe_eval_expr(expr: str):
    """Evaluate a pure arithmetic expression safely using AST."""
    node = ast.parse(expr, mode='eval')

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Num):  
            return n.n
        if isinstance(n, ast.Constant):  
            if isinstance(n.value, (int, float)):
                return n.value
        if isinstance(n, ast.BinOp):
            if not isinstance(n.op, ALLOWED_BINOPS):
                raise ValueError("Operator not allowed")
            l, r = _eval(n.left), _eval(n.right)
            if isinstance(n.op, ast.Add): return l + r
            if isinstance(n.op, ast.Sub): return l - r
            if isinstance(n.op, ast.Mult): return l * r
            if isinstance(n.op, ast.Div): return l / r
            if isinstance(n.op, ast.Mod): return l % r
            if isinstance(n.op, ast.Pow): return l ** r
            if isinstance(n.op, ast.FloorDiv): return l // r
        if isinstance(n, ast.UnaryOp):
            if not isinstance(n.op, ALLOWED_UNARYOPS):
                raise ValueError("Unary op not allowed")
            val = _eval(n.operand)
            if isinstance(n.op, ast.UAdd): return +val
            if isinstance(n.op, ast.USub): return -val
        raise ValueError(f"Unsupported node {type(n)}")

    return _eval(node)


def parse_and_compute(query: str):
    q = query.lower().replace("compute:", "").strip()
    parts = [p.strip() for p in re.split(r'\band\b', q)]

    results = []
    for part in parts:
        # Handle "15% of 640"
        match = re.match(r'(\d+(\.\d+)?)\s*% of\s*(\d+(\.\d+)?)', part)
        if match:
            perc = float(match.group(1)) / 100.0
            num = float(match.group(3))
            expr = f"({perc} * {num})"
            val = safe_eval_expr(expr)
            results.append(f"{match.group(0)} = {int(val) if val.is_integer() else val}")
            continue

        try:
            val = safe_eval_expr(part)
            if isinstance(val, (int, float)) and float(val).is_integer():
                val = int(val)
            results.append(f"{part} = {val}")
        except Exception as e:
            results.append(f"Could not evaluate '{part}': {e}")

    return "; ".join(results)
