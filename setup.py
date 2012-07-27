import os
from distutils.core import setup

setup(name="Sweave2knitr",
      author="David Robinson",
      author_email="dgrtwo@princeton.edu",
      description="Convert an Sweave document to work in knitr",
      packages=["Sweave2knitr"],
      package_dir={"Sweave2knitr": os.path.join("src", "Sweave2knitr")},
      version="0.1",
      scripts=[os.path.join("scripts", "Sweave2knitr")],
      )
