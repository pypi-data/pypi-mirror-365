# TaxonLib

This library contains tools that are useful for working with taxonomy information. 
This library was specifically designed to facilitate 
the creation and analysis of taxa files 
that are intended to be used as 
input for the Naturalis AI deep learning pipeline.

## Precommit gitleaks

This project has been protected by [gitleaks](https://github.com/gitleaks/gitleaks).
The pipeline is configured to scan on leaked secrets.

To be sure you do not push any secrets,
please [follow our guidelines](https://docs.aob.naturalis.io/standards/secrets/),
install [precommit](https://pre-commit.com/#install)
and run the commands:

- `pre-commit autoupdate`
- `pre-commit install`