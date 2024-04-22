# `bibfmt`

```sh
bibfmt in.bib
```

allows you to apply consistent formatting to you BibTeX file:

```console
$ bibfmt --help
usage: bibfmt [options] [<infiles>...]

Format BibTeX files.

positional arguments:
  infiles               input BibTeX files (default: stdin)

options:
  -h, --help            show this help message and exit
  --version, -v         display version information
  -i, --in-place        modify infile in place
  --drop DROP           drops field from bibtex entry if they exist, can be passed multiple times

Formatting:
  -b, --sort-by-bibkey  sort entries by BibTeX key (default: false)
  --indent INDENT       how to indent the entries.
                        Specify e.g. `4` for 4 spaces or `tab` (default: 2 spaces)
  -d {braces,quotes}, --delimiter-type {braces,quotes}
                        which delimiters to use in the output file (default: braces {...})
  --doi-url-type {unchanged,new,short}
                        DOI URL (new: https://doi.org/<DOI> (default), short: https://doi.org/abcde)
  -p SEP, --page-range-separator SEP
                        page range separator (default: --)
```

### Similar software

- [bibcure](https://github.com/bibcure/bibcure)
- [betterbib](https://githib.com/texworld/betterbib)
