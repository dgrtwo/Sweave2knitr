"""
Unit tests for Sweave2knitr script
"""

import re
import unittest
import warnings

from Sweave2knitr import converter


### TEXT BLOCK ###
## used for testing

txt1 = r"""
\usepackage{hyperref}
\usepackage{natbib, Sweave}

\SweaveOpts{results=tex, echo=false}

<<echo=false>>=
library(somelib)
setCacheDir("cache")
@

<<named_chunk, results=hide, fig=TRUE>>=
# R code here
@

<<keep.source=TRUE, term=TRUE>>=
@

LaTeX can include commands like \SomeCommand{arg} with arguments, or without
like \this.
"""


class TestConverter(unittest.TestCase):
    """
    Tests for the SweaveConverter class, which converts Sweave LaTeX to knitr
    """
    def test_parsing(self):
        """Provide simple examples of noweb LaTeX"""
        p = converter.SweaveConverter(txt=txt1)

        # check warning for dropped option
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = p.convert_knitr()
            self.assertEqual(len(w), 1)
            self.assertTrue("term" in str(w[0].message))

        self.assertTrue("Sweave" not in result)
        Sexpr_line = ("\\Sexpr{opts_chunk$set(results='asis',echo=FALSE," +
                    "message=FALSE)}")

        spaceless_result = result.replace(" ", "")
        self.assertTrue(Sexpr_line in spaceless_result)

        self.assertTrue("<<echo=FALSE>>=" in result)
        self.assertTrue("<<tidy=FALSE>>=" in result)
        self.assertTrue("<<named_chunk,results='hide',keep.fig='high'>>="
                            in spaceless_result)

        # check that text and R code remains
        self.assertTrue(r"like \SomeCommand{arg} with" in result)
        self.assertTrue("# R code here")

        # check that we got rid of cacheSweave line
        self.assertTrue("setCacheDir" not in result)

        # should be missing only two lines: setCacheDir and \usepackage{Sweave}
        self.assertTrue(len(result.split("\n")), len(txt1.split("\n")) - 2)


if __name__ == "__main__":
    unittest.main()
