moonshine-wrangler
==================

Based on the 'samplemod' sample module project discussed by Kenneth Reitz.

`Learn more <https://kennethreitz.org/essays/2013-01-repository_structure_and_python>`_.

Notes on coding style for this project
--------------------------------------

This project will attempt to follow PEP-8 with the following exception:

- `The maximum line length constraint <https://pep8.org/#maximum-line-length>`_ 
  will not be enforced.  
  Lines up to 100 characters will be tolerated unconditionally.
  Lines up to 140 characters will be tolerated if the maintainer considers that 
  a single long line is considered more readable than multiple lines of 100 
  characters or less.

At the time of writing, requirements.txt makes both pycodestyle and flake8 
available for style enforcement.  A decision will be made at some later
time in relation to whether one of these or some other tool is used as 
the primary enforcement method.



