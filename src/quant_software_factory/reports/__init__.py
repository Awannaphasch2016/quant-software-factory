"""Client report builders.

Each report type lives in its own subpackage and is run as a module, for example
``python -m quant_software_factory.reports.returns_transactions``. This package
deliberately imports nothing so that running a subpackage with ``-m`` does not
pre-import it.
"""
