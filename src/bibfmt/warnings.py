from __future__ import annotations


class UnsupportedType(Warning):
    """Base Warning for trying to handle an unsupported type"""

    pass


class UnsupportedBibTeXType(UnsupportedType):
    """Warning for an unsupported BibTeX type"""

    pass


class UnsupportedBibLaTeXType(UnsupportedType):
    """Warning for an unsupported BibLaTeX type"""

    pass
