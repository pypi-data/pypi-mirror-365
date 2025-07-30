from taxonlib.canonical_name import canonize
from taxonlib.tools.taxa import QualifiedName


class TaxonType(object):

    def __init__(self, taxon_type: str, canonical_name: str, search_name: str):
        self.search_name = search_name
        self.canonical_name = canonical_name
        self.full_type = taxon_type

    @property
    def main_type(self) -> str:
        return self.full_type.split("_")[0]

    def __str__(self):
        return f"type = {self.full_type}, canonical name = {self.canonical_name}, search name = {self.search_name}"


def get_type(qualified_name: QualifiedName) -> TaxonType:
    type_ = "unknown"
    taxon_name_org = qualified_name.scientific_name
    taxon_name = canonize(taxon_name_org)
    tokens = taxon_name.split()
    search_name = taxon_name
    try:
        if int(taxon_name[-4:]):  # ends with year
            return TaxonType("malformed_format", taxon_name, taxon_name)
    except ValueError:
        pass
    if "x" in tokens or "×" in tokens or "×" in taxon_name:
        type_ = "hybrid"
        if "'" in taxon_name:
            type_ += "_cultivar"
        elif tokens[-1] in ["×", "x"]:
            type_ += "_spec"
    else:
        match taxon_name.split():
            case [higher]:
                type_ = "higher"
                if "/" in higher:
                    type_ = "aggregate_multiplet"
                else:
                    if taxon_name in ["Plantae", "Fungi", "Animalia"]:
                        type_ += "_kingdom"
                    elif taxon_name.endswith("dae"):
                        type_ += "_family"
                    elif taxon_name.endswith("nae"):
                        type_ += "_subfamily"
                    elif taxon_name.endswith("ini"):
                        type_ += "_tribe"
            case [genus, species]:
                type_ = "species"
                if species.startswith("(") and species.endswith(")"):  # subgenus
                    type_ = "higher"
                elif "/" in species:
                    type_ = "aggregate_multiplet"
                if taxon_name_org.split()[1].startswith("("):  # species with subgenus
                    type_ += "_subgenus"
                # print(genus, species)
            case [genus, species, *infra_epithet]:
                infra_epithet = " ".join(infra_epithet)
                search_name = genus + " " + species
                if "gr." in infra_epithet:
                    type_ = "aggregate_group"
                elif "sl." in infra_epithet:
                    type_ = "aggregate_sensu_lato"
                elif "agg." in infra_epithet:
                    type_ = "aggregate_agg"
                elif "/" in infra_epithet or "/" in species:
                    type_ = "aggregate_multiplet"
                elif "+" in taxon_name:
                    type_ = "aggregate_other"
                else:
                    type_ = "infra"
                    if "'" in " ".join(infra_epithet):
                        type_ += "_cultivar"
                    else:
                        infra_modifiers = [
                            "var.",
                            "subsp.",
                            "teleomorf",
                        ]  # TODO: consider alternative spellings
                        for token in tokens:
                            if token in infra_modifiers:
                                type_ += f"_{token.replace('.', '')}"
                        if "_" not in type_:  # e.g. Lamiastrum galeobdolon argentatum
                            type_ += "_subsp"

    return TaxonType(type_, canonize(taxon_name), search_name)
