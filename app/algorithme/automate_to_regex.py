def automate_to_regex(states, initial_state, final_states, transitions):
    """
    Convertit un automate fini en expression régulière en utilisant l'algorithme d'élimination d'états.
    
    Args:
        states: Liste des états de l'automate
        initial_state: État initial
        final_states: Liste des états finaux
        transitions: Dictionnaire des transitions {état_source: {symbole: [états_destination]}}
    
    Returns:
        Expression régulière équivalente à l'automate
    """
    
    def normalize_transitions(transitions):
        """Normalise les transitions pour s'assurer que les destinations sont des listes"""
        norm = {}
        for src, sym_dict in transitions.items():
            src = str(src)
            norm[src] = {}
            for sym, dests in sym_dict.items():
                if isinstance(dests, str):
                    dest_list = [dests]
                elif isinstance(dests, list):
                    dest_list = dests
                else:
                    dest_list = [str(dests)]
                norm[src][sym] = [str(d) for d in dest_list]
        return norm
    
    def concat(r1, r2):
        """Concatène deux expressions régulières"""
        if not r1 or r1 == "∅":
            return r2 if r2 else "∅"
        if not r2 or r2 == "∅":
            return r1 if r1 else "∅"
        if r1 == "ε":
            return r2
        if r2 == "ε":
            return r1
        
        # Ajouter des parenthèses si nécessaire pour la concaténation
        def needs_parens_for_concat(expr):
            if len(expr) <= 1:
                return False
            if expr.startswith("(") and expr.endswith(")") and is_balanced_parens(expr):
                return False
            if expr.endswith("*"):
                return False
            return "+" in expr
        
        result_r1 = f"({r1})" if needs_parens_for_concat(r1) else r1
        result_r2 = f"({r2})" if needs_parens_for_concat(r2) else r2
        
        return result_r1 + result_r2
    
    def union(r1, r2):
        """Fait l'union de deux expressions régulières"""
        if not r1 or r1 == "∅":
            return r2 if r2 else "∅"
        if not r2 or r2 == "∅":
            return r1 if r1 else "∅"
        if r1 == r2:
            return r1
        
        # Séparer les alternatives et éviter les doublons
        alts1 = set(split_alternatives(r1))
        alts2 = set(split_alternatives(r2))
        all_alts = sorted(alts1.union(alts2))
        
        if len(all_alts) == 1:
            return all_alts[0]
        return "+".join(all_alts)
    
    def split_alternatives(expr):
        """Divise une expression en alternatives (gestion correcte des parenthèses)"""
        if not expr or expr == "∅":
            return []
        
        alternatives = []
        current = ""
        paren_count = 0
        
        for char in expr:
            if char == "+" and paren_count == 0:
                if current:
                    alternatives.append(current)
                current = ""
            else:
                if char == "(":
                    paren_count += 1
                elif char == ")":
                    paren_count -= 1
                current += char
        
        if current:
            alternatives.append(current)
        
        return alternatives
    
    def is_balanced_parens(expr):
        """Vérifie si les parenthèses sont équilibrées"""
        count = 0
        for char in expr:
            if char == "(":
                count += 1
            elif char == ")":
                count -= 1
                if count < 0:
                    return False
        return count == 0
    
    def kleene_star(r):
        """Applique la fermeture de Kleene"""
        if not r or r == "∅":
            return "ε"
        if r == "ε":
            return "ε"
        if r.endswith("*"):
            return r
        if len(r) == 1:
            return r + "*"
        
        # Ajouter des parenthèses si nécessaire
        if r.startswith("(") and r.endswith(")") and is_balanced_parens(r):
            return r + "*"
        return f"({r})*"
    
    def simplify_regex(expr):
        """Simplifie l'expression régulière finale"""
        if not expr:
            return "∅"
        
        # Remplacer les patterns vides
        expr = expr.replace("ε+", "").replace("+ε", "")
        
        # Nettoyer les + multiples
        while "++" in expr:
            expr = expr.replace("++", "+")
        
        # Nettoyer les + en début/fin
        expr = expr.strip("+")
        
        if not expr:
            return "∅"
        if expr == "ε":
            return "ε"
        
        return expr
    
    # Normalisation des entrées
    states = [str(s) for s in states]
    initial_state = str(initial_state)
    final_states = [str(f) for f in final_states]
    transitions = normalize_transitions(transitions)
    
    # Cas particuliers
    if not final_states:
        return "∅"
    
    # États auxiliaires
    S, F = "START", "FINAL"
    all_states = [S] + states + [F]
    
    # Initialisation de la matrice des expressions régulières
    R = {}
    for i in all_states:
        R[i] = {}
        for j in all_states:
            R[i][j] = "∅"
    
    # Remplissage avec les transitions existantes
    for src in states:
        if src in transitions:
            for sym, dests in transitions[src].items():
                for dest in dests:
                    if dest in states:
                        R[src][dest] = union(R[src][dest], sym)
    
    # Transition ε de START vers l'état initial
    R[S][initial_state] = "ε"
    
    # Transitions ε des états finaux vers FINAL
    for f in final_states:
        R[f][F] = "ε"
    
    # Élimination des états intermédiaires
    states_to_eliminate = [q for q in states]
    
    for k in states_to_eliminate:
        # Calculer les nouvelles transitions avant d'éliminer k
        new_transitions = {}
        
        for i in all_states:
            if i == k:
                continue
            for j in all_states:
                if j == k:
                    continue
                
                # Calculer R_ij = R_ij + R_ik(R_kk)*R_kj
                r_ik = R[i][k]
                r_kk = R[k][k]
                r_kj = R[k][j]
                
                if r_ik != "∅" and r_kj != "∅":
                    # Construction de R_ik(R_kk)*R_kj
                    middle_part = kleene_star(r_kk)
                    new_path = concat(concat(r_ik, middle_part), r_kj)
                    new_transitions[(i, j)] = union(R[i][j], new_path)
                else:
                    new_transitions[(i, j)] = R[i][j]
        
        # Appliquer les nouvelles transitions
        for (i, j), new_val in new_transitions.items():
            R[i][j] = new_val
        
        # Éliminer l'état k
        for i in all_states:
            R[i][k] = "∅"
            R[k][i] = "∅"
    
    # Récupérer le résultat final
    result = R[S][F]
    result = simplify_regex(result)
    
    return result


