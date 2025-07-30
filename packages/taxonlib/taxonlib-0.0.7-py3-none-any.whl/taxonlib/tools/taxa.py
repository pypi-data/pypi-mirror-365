from taxonlib.canonical_name import canonize

ranks = ["kingdom", "division", "class", "order", "family", "genus"]
remove_modifiers = []


class EmptyGbifRecord(Exception):
    pass


def remove_author(name):
    # remove years at end of taxon, e.g. Hydraena, 1999
    comma_elements = name.split(",")
    try:
        has_year_at_end = int(comma_elements[-1].strip())
    except ValueError:
        has_year_at_end = False
    if has_year_at_end:
        name = ",".join(comma_elements[:-1])

    #
    elements = name.split()
    start_parenthesis = None
    end_parenthesis = None
    start_author = len(elements)
    for e, element in enumerate(elements):
        parenthesized_content = ""
        if e > 0:
            if (
                element in ["von", "da", "van", "de", "den", "hort."]
                or element.startswith("d'")
            ) and start_parenthesis is None:
                start_author = e
                break

            if element.startswith("("):
                parenthesized_content += element
                start_parenthesis = e
            elif start_parenthesis:
                parenthesized_content += element

            if start_parenthesis and (
                element.endswith(")")
                or element.endswith("),")
                or element.endswith(")]")
            ):
                parenthesized_content += element
                end_parenthesis = e
            elif (
                element[0].isupper()
                and not start_parenthesis
                and not elements[e - 1] in ["x", "×"]
            ):
                start_author = e
                break

            if start_parenthesis and end_parenthesis:
                is_author = True
                for e_par in range(start_parenthesis, end_parenthesis + 1):
                    if elements[e_par] == "x":
                        is_author = False
                        break
                if is_author:
                    start_author = start_parenthesis
                    break

    if start_parenthesis and not end_parenthesis:
        raise ValueError(f"found unclosed parenthesis in '{name}'")
    if not start_parenthesis and end_parenthesis:
        raise ValueError(f"found unstarted parenthesis in '{name}'")

    return " ".join(elements[:start_author])


class QualifiedName(object):
    def __init__(self, scientific_name: str, namespace: str, source_id: str) -> None:
        super().__init__()
        self.source_id = source_id
        self.namespace = namespace
        self.scientific_name = scientific_name

    def __str__(self):
        return f"{self.scientific_name}:{self.namespace}:{self.source_id}"

    @staticmethod
    def from_str(input_: str):
        try:
            scientific_name, namespace, source_id = input_.split(":")
        except ValueError:
            print(input_)
            raise
        return QualifiedName(scientific_name, namespace, source_id)

    @property
    def qualified_id(self):
        return f"{self.namespace}:{self.source_id}"

    @property
    def canonical_name(self):
        return canonize(self.scientific_name)
