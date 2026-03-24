import ast
import operator as op
import re
import sqlite3
from typing import Any, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup

operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
}


def eval_expr(expr: str) -> float:
    def eval_(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return operators[type(node.op)](eval_(node.left), eval_(node.right))
        elif isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](eval_(node.operand))
        else:
            raise TypeError(node)

    return eval_(ast.parse(expr, mode="eval").body)


def csv_sql(sql: str, csv_path: str) -> Dict[str, Any]:
    """Run read-only SQL over the uploaded trips."""
    try:
        df = pd.read_csv(csv_path)
        conn = sqlite3.connect(":memory:")
        df.to_sql("trips", conn, index=False)
        result_df = pd.read_sql_query(sql, conn)
        rows = result_df.to_dict(orient="records")
        conn.close()
        return {
            "success": True,
            "data": {"rows": rows, "row_count": len(rows), "source": "uploaded.csv"},
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def policy_retriever(url: str, query: str = "", k: int = 5) -> Dict[str, Any]:
    """Fetch the pricing page URL, extract text, and return short, quotable snippets."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text(separator=" ", strip=True)
        passages = [p.strip() for p in text.split(".") if len(p.strip()) > 20]

        if query:
            query_terms = query.lower().split()
            scored_passages = []
            for p in passages:
                score = sum(1 for term in query_terms if term in p.lower())
                if score > 0:
                    scored_passages.append({"text": p, "source": url, "score": score})

            scored_passages.sort(key=lambda x: x["score"], reverse=True)
            results = scored_passages[:k]
        else:
            results = [{"text": p, "source": url, "score": 1} for p in passages[:k]]

        return {"success": True, "data": {"passages": results}}
    except Exception as e:
        return {"success": False, "error": str(e)}


def calculator(expression: str, units: str = "") -> Dict[str, Any]:
    """Safe arithmetic (no eval)."""
    if not re.match(r"^[0-9+\-*/().\s]+$", expression):
        return {
            "success": False,
            "error": (
                "Invalid characters in expression."
                " Only digits and operators (+ - * /) allowed."
            ),
        }

    try:
        val = eval_expr(expression)
        res = {"value": val}
        if units:
            res["units"] = units
        return {"success": True, "data": res}
    except Exception as e:
        return {"success": False, "error": str(e)}
