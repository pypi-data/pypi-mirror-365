remove_modifiers = ["spec.", "indet.", "sp."]
sensu_lato_alternatives = ["s.l.", "sl", "sl.", "sensu lato", "s. lat.", "s.lat."]
sensu_stricto_alternatives = ["s.s.", "ss.", "s. str."]
group_alternatives = ["group", "gr", "gr."]
forma_alternatives = ["f.", "f", "forma"]
interpunction_to_separate = [","]


def canonize(taxon_name: str):
    # change sensu lato/stricto forms to ones without spaces to make parsing easier
    for alternative in sensu_lato_alternatives:
        if " " in alternative:
            taxon_name = taxon_name.replace(alternative, "s.l.")
    for alternative in sensu_stricto_alternatives:
        if " " in alternative:
            taxon_name = taxon_name.replace(alternative, "s.s.")

    tokens = taxon_name.split()
    new_tokens = []

    for t, token in enumerate(tokens):
        interpunction_found = False
        is_subgenus_spec = None
        # e.g. Chorthippus (Chorthippus) *.
        subgenus_found = t == 1 and token.startswith("(") and token.endswith(")")
        if subgenus_found:
            if len(tokens) > 2:
                is_subgenus_spec = (
                    "." in tokens[2]
                )  # e.g. Chorthippus (Chorthippus) spec., Arion (Arion) agg.
            else:
                is_subgenus_spec = True  # e.g. Chorthippus (Chorthippus)
        for interpunction in interpunction_to_separate:
            if interpunction in token:
                new_tokens.extend(
                    token.replace(interpunction, f" {interpunction} ").split()
                )
                interpunction_found = True
                break
        if (
            not interpunction_found  # interpunction attached to tokens is dealt with above
            and (
                not subgenus_found  # remove subgenus
                or is_subgenus_spec  # unless it's a spec.
            )
        ):
            new_tokens.extend([token])
    tokens = new_tokens
    #
    new_tokens = []
    for t, token in enumerate(tokens):
        # remove the dash before group representations
        for group_alternative in group_alternatives:
            if group_alternative in token and "-" in token:
                token = token.replace("-", " ").replace(group_alternative, "gr.")
        new_tokens.append(token)
    tokens = new_tokens
    #
    if "x" in tokens or "×" in tokens or "×" in taxon_name:  # hybrids
        if "x" in tokens:
            cross_index = tokens.index("x")
            for i, token in enumerate(tokens):
                if token == "x":
                    tokens[i] = "×"
        elif "×" in tokens:
            cross_index = tokens.index("×")
        else:
            new_tokens = []
            for token in tokens:
                if "×" in token:
                    new_tokens.append("×")
                    new_tokens.append(token[1:])
                else:
                    new_tokens.append(token)
            tokens = new_tokens
            cross_index = tokens.index("×")
        # check if the hybrid is described in parentheses
        end_parenthesis = None
        start_parenthesis = None
        start = " ".join(tokens[:cross_index]).strip()
        rest = tokens[cross_index + 1 :]
        if len(rest) > 1 and rest[1].startswith("("):
            start_parenthesis = 1
            for t, token in enumerate(rest):
                if token.endswith(")"):
                    end_parenthesis = t

        if end_parenthesis:
            # removes the part between parentheses
            rest = rest[:start_parenthesis] + rest[end_parenthesis + 1 :]
        # check if hybrid is described using =
        # Quercus cerris x suber = Q. x crenata
        if "=" in tokens:
            select_tokens = tokens[tokens.index("=") + 1 :]
            if "." in select_tokens[0]:
                select_tokens[0] = tokens[0]
            tokens = " ".join(select_tokens).strip().split()
        else:
            tokens = (start + " × " + " ".join(rest).strip()).split()

    out = []
    for token in tokens:
        if token not in remove_modifiers:
            if token.lower() in sensu_lato_alternatives:
                token = "sl."
            elif token.lower() in sensu_stricto_alternatives:
                token = "ss."
            elif token.lower() in forma_alternatives:
                token = "forma"
            elif token.lower() in group_alternatives:
                token = "gr."
            out.append((token.replace("hybrid", "×") if token == "hybrid" else token))
    return " ".join(out)


alternative_replacements = {
    "forma": "",
    "var.": "",
    "subsp.": "",
    "f.": "",
    "form": "",
    "group": "gr.",
}


def alternatives_match(taxon_name1: str, taxon_name2: str):
    alternative1 = make_alternative(taxon_name1)
    alternative2 = make_alternative(taxon_name2)
    return alternative1 == alternative2


def make_alternative(taxon_name, do_canonize: bool = True):
    if do_canonize:
        taxon_name = canonize(taxon_name)
    tokens_out = []
    tokens = taxon_name.split()
    for t, token in enumerate(tokens):
        if t == 1 and token == "×" and len(tokens) > 2:
            pass
        else:
            tokens_out.append(alternative_replacements.get(token, token))
    return " ".join([t_ for t_ in tokens_out if len(t_) > 0])
