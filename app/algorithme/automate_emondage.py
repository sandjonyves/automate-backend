from .automate_analysis import identify_states

def emonder_automate(automaton_type,is_deterministic,states, initial_state, final_states, transitions, alphabet):
    result = identify_states(states, initial_state, final_states, transitions)
    utiles = set(result["utiles"])

    # Normaliser les transitions
    norm_trans = {}
    for src, sym_dict in transitions.items():
        if src not in utiles:
            continue
        norm_trans[src] = {}
        for sym, dests in sym_dict.items():
            norm_dests = [str(d) for d in (dests if isinstance(dests, list) else [dests])]
            filtered_dests = [d for d in norm_dests if d in utiles]
            if filtered_dests:
                norm_trans[src][sym] = filtered_dests

    return {
        "automaton_type":automaton_type,
        "is_deterministic":is_deterministic,
        "states": sorted(list(utiles)),
        "alphabet": list(alphabet),
        "initial_state": initial_state if initial_state in utiles else None,
        "final_states": [f for f in final_states if f in utiles],
        "transitions": norm_trans
    }
