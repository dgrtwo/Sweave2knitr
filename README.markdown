Sweave2knitr
============

Sweave2knitr is a simple Python script that helps to convert [Sweave](http://www.statistik.lmu.de/~leisch/Sweave/) LaTeX documents to be instead compatible with Yihui Xie's [knitr](http://yihui.name/knitr/) package. It is based on and inspired by Jeromy Anglim's blog entry [ Converting Sweave LaTeX to knitr LaTeX: A case study ](http://jeromyanglim.blogspot.com/2012/06/converting-sweave-latex-to-knitr-latex.html).

*Warning:* This conversion is not an exact science. While this catches some of the most common issues faced when converting from Sweave to LaTeX, there are a virtually infinite number of special cases that will have to be handled. Furthermore, this is a very early version that has been tested on only a few documents. Try it on your own Sweave documents: contributions are *strongly* encouraged!

Installation
------------

You can install Sweave2knitr from the [Python Package Index](http://pypi.python.org/pypi) using:

    easy_install Sweave2knitr

or using pip:

    pip install Sweave2knitr

(On Linux or Macs, you might need to add `sudo` to the start of each command). You can also install it from source:

    python setup.py build
    python setup.py install

Usage
-----

If `infile.Rnw` is your Sweave LaTeX file, use

    Sweave2knitr infile.Rnw outfile.nw

You can then use

    Rscript -e "library(knitr); knit('outfile.nw', 'outfile.tex')"
    pdflatex outfile.tex

To create the .tex file and turn it into a PDF.
