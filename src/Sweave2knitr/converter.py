"""
Contains parser to tokenize Sweave LaTeX and turn it into a format compatible
with knitr.
"""

import re
import warnings


### PARAMETERS ###

# define the pattern of tokens in a noweb file
# The tokens that we might want to convert are code chunks and LaTeX
# commands

pattern = "(?:" + "|".join([
        r"[\n\r](<<.*?>>=.*?[\n\r]@)",     # code chunk
        r"(\\[^\s]*{.*?})",          # command
]) + ")"

DROPPED_OPTIONS = ["term", "prefix", "stripe.white"]

OPTION_MAPPINGS = {"prefix.string": "fig.path",
                   "width": "fig.width", "height": "fig.height"}

PAIR_MAPPINGS = {("fig", "TRUE"): ("keep.fig", "'high'"),
                 ("fig", "FALSE"): ("keep.fig", "'none'"),
                 ("keep.source", "TRUE"): ("tidy", "FALSE"),
                 ("keep.source", "FALSE"): ("tidy", "TRUE")}


### FUNCTIONS ###

def _convert_knitr_option(key, value):
    """
    Convert a single option to knitr format. Return None if the option
    should be dropped. This will get rid of whitespace around the key and value
    """
    key, value = key.strip(), value.strip()
    if value == "":
        # no conversion necessary
        return (key, value)

    for orig, repl in [("tex", "asis"), ("true", "TRUE"), ("false", "FALSE")]:
        value = value.replace(orig, repl)

    if ("TRUE" not in value and "FALSE" not in value
        and not re.match("\d+$", value)):
        if not value.startswith("'"):
            value = "'" + value
        if not value.endswith("'"):
            value = value + "'"

    k, v = key.strip(), value.strip()

    if k in OPTION_MAPPINGS:
        k = OPTION_MAPPINGS[k]

    if k in DROPPED_OPTIONS:
        warnings.warn("Dropping option %s, unsupported in knitr" % k)
        return None

    if (k, v) in PAIR_MAPPINGS:
        k, v = PAIR_MAPPINGS[(k, v)]

    return k, v


def _convert_knitr_options(args):
    """
    convert a list of options to an Sweave code chunk (or SweaveOpts) to
    knitr format
    """
    converted = [_convert_knitr_option(*a) for a in args]
    fixed_args = [("=".join(a) if a[1] != ""
                                else a[0])
                            for a in converted if a != None]
    fixed_args = [a for a in fixed_args if a != None]

    # check for special case of print=FALSE, term=FALSE
    stripped = [map(str.strip, o) for o in fixed_args]
    if ("print", "FALSE") in stripped and ("term", "FALSE") in stripped:
        fixed_args = ([(k, v) for k, v in fixed_args
                        if k not in ("print", "term")] +
                            [("results", "'hide'")])

    return fixed_args


### Token types ###

class Token(object):
    """Represents any kind of token in a LaTeX noweb file"""
    pass


class CodeChunkToken(Token):
    """A Sweave code chunk"""
    def __init__(self, txt):
        """Given the text of the code chunk"""
        options, self.rest = re.search("<<(.*?)>>=(.*)", txt,
                                        re.DOTALL).groups()
        self.options = re.findall("([^<> ,\=]+)\s*=?\s*([^<> ,]*)", options)

    def convert_knitr(self):
        """
        Write as a knitr code chunk- fix options, put in quotes, remove lines
        of code that make sense only in Sweave (like setCacheDir)
        """
        rest = "\n".join([l for l in self.rest.split("\n")
                            if "setCacheDir" not in l])

        return "\n<<%s>>=%s" % (",".join(_convert_knitr_options(self.options)),
                                        rest)


class CommandToken(Token):
    """Represents a LaTeX command with arguments"""
    def __init__(self, txt):
        """
        initialized with the text of a LaTeX command, from the backslash
        to the }
        """
        self.command, args = re.match(r"\\(.*){(.*)}", txt, re.DOTALL).groups()
        self.args = args.split(",")

    def convert_knitr(self):
        """
        Convert the command to a knitr version. In particular, check if it is
        \usepackage{Sweave} or \SweaveOpts
        """
        command, args = self.command, self.args[:]

        # remove the Sweave package
        if self.command == "usepackage":
            args = [a for a in args if "Sweave" not in a]
            if len(args) == 0:
                return None
            args[0] = args[0].lstrip()

        # replace SweaveOpts with knitr version
        if self.command == "SweaveOpts":
            command = "Sexpr"
            newargs = _convert_knitr_options([a.split("=") for a in args])
            newargs.append(" message=FALSE")
            args = ["opts_chunk$set(%s)" % ",".join(newargs)]

        return r"\%s{%s}" % (command, ",".join(args))


class RegularTextToken(Token):
    """Any region that doesn't have to be converted"""
    def __init__(self, txt):
        self.txt = txt

    def convert_knitr(self):
        """Return without changing anything"""
        return self.txt


class SweaveConverter(object):
    """Parses noweb LaTeX and handles conversion to knitr"""
    def __init__(self, infile=None, txt=None):
        """Given either an input file or text"""
        if infile == None and txt == None:
            raise ValueError("NowebParser must be given either an input " +
                             "file or text")
        if infile:
            with open(infile) as inf:
                txt = inf.read()
        self.txt = txt

        self.tokens = self.tokenize_noweb(txt)

    def tokenize_noweb(self, txt):
        """Tokenizes noweb LaTeX"""
        matches = [(m.group(m.lastindex), m.lastindex, m.start(), m.end())
                        for m in re.finditer(pattern, txt, re.DOTALL)]

        token_classes = [CodeChunkToken, CommandToken]
        tokens = []
        last_end = 0
        for match, tokentype, s, e in matches:
            if last_end != s:
                tokens.append(RegularTextToken(txt[last_end:s]))
            tokens.append(token_classes[tokentype - 1](match))
            last_end = e
        tokens.append(RegularTextToken(txt[last_end:]))

        return tokens

    def convert_knitr(self, outfile=None):
        """Return as knitr LaTeX. If an output file is given, write to it"""
        txt = "".join([s for s in [t.convert_knitr() for t in self.tokens]
                            if s != None])
        if outfile != None:
            with open(outfile, "w") as outf:
                outf.write(txt)
        return txt
