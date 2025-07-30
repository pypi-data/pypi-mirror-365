import os
from dataclasses import dataclass


@dataclass
class Source(object):
    images_path: str
    taxa_path: str
    out_folder: str
    identifier: str
    namespace: str

    @property
    def counts_path(self):
        return os.path.join(self.out_folder, "taxon_counts.csv")

    @property
    def custom_preprocessed_taxa_path(self):
        return os.path.join(self.out_folder, "taxa_custom_preproc.csv")
