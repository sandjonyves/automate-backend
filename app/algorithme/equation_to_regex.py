import re

def arden_resolution(equations: dict, start: str) -> str:
    # Pour simplifier : on fait des substitutions successives
    eqs = equations.copy()

    # On itère en remplaçant les variables dans chaque équation
    variables = list(eqs.keys())
    for var in reversed(variables):
        expr = eqs[var]
        for v in variables:
            if v != var:
                expr = expr.replace(v, f"({eqs.get(v, '')})")
        # simplification par méthode d'Arden si forme AX + B
        match = re.fullmatch(r'(.+)\*?' + var + r'(.+)?', expr.replace(' ', ''))
        if match:
            A = match.group(1)
            B = match.group(2) or ""
            expr = f"({A})*{B}"
        eqs[var] = expr

    return eqs[start]
