import ast

ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv)
ALLOWED_UNARYOPS = (ast.UAdd, ast.USub)

def safe_eval_expr(expr: str):
    node = ast.parse(expr, mode='eval')

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Num):
            return n.n
        if isinstance(n, ast.BinOp):
            if not isinstance(n.op, ALLOWED_BINOPS): raise ValueError("Bad op")
            l, r = _eval(n.left), _eval(n.right)
            if isinstance(n.op, ast.Add): return l + r
            if isinstance(n.op, ast.Sub): return l - r
            if isinstance(n.op, ast.Mult): return l * r
            if isinstance(n.op, ast.Div): return l / r
            if isinstance(n.op, ast.Mod): return l % r
            if isinstance(n.op, ast.Pow): return l ** r
            if isinstance(n.op, ast.FloorDiv): return l // r
        if isinstance(n, ast.UnaryOp):
            if not isinstance(n.op, ALLOWED_UNARYOPS): raise ValueError("Bad unary")
            val = _eval(n.operand)
            if isinstance(n.op, ast.UAdd): return +val
            if isinstance(n.op, ast.USub): return -val
        raise ValueError(f"Unsupported node {type(n)}")
    return _eval(node)
