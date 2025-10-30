moonshine-wrangler
==================


Meaning of the project name
---------------------------

The software delivered in this project is intended for use on bodies of data
captured when operating with modelling guitar amplifiers manufactured by the 
Fender Musical Instruments Corporation (FMIC).

The amplifiers this software applies to are (mostly) sold under different 
subranges of FMIC's 'Mustang' registered trade mark, notably the following 
series/models:

- Fender Mustang I, II, III, IV and V (and v2 variants of those)
- Fender Mustang LT-25, LT-50, LT-40S and Fender Rumble LT-25
- Fender Mustang Micro Plus

Each of the three major groups identified above each have their own serialization 
format for amplifier preset definitions (i.e. a configuration which enables the 
host digital amplifier to model the behaviour of a specific analog amplifier/effect 
set).

Although the formats differ from series to series they are are closely related in 
content and structure.  Part of the purpose of the library is to enable presets 
serialized from one hardware series to be deployed to devices of another series, 
and this is done by 'distilling' the content to a minimal series-neutral format
and then 'remixing' the distilled data into the series-specific format of the 
target device.  

The 'moonshine' component of the name is intended to evoke the 
distill/remix aspect of the library.

The 'wrangler' component of the name is (obviously) intended to refer to working
with Mustang series amps without making direct reference in the name to FMIC's 
registered trade mark.

The maintenance of this project is completely independent from FMIC, and will 
be vigilant in avoiding any violation of FMIC's intellectual property rights 
in relation to trademarks or copyright in the software deployed in their devices.

Notes on coding style for this project
--------------------------------------

This project will attempt to follow PEP-8 with the following exception:

- `The maximum line length constraint <https://pep8.org/#maximum-line-length>`_ 
  will not be enforced.  
  Lines up to 100 characters will be tolerated unconditionally.
  Lines up to 200 characters will be tolerated if the maintainer considers that 
  a single long line is considered more readable than multiple lines of 100 
  characters or less.
  Longer lines may be tolerated for appropriately strong reasons (e.g. URLs)

PEP-8 does not make a recommendation in relation to usage of single- and double-
quote characters around strings, but does contain an exhortation to make a rule
and stick to it.

As a former C/C++ programmer, I prefer to use double-quotes to enclose
strings in Python as this matches the meaning of the character in C/C++, 
and single-quotes have a different meaning in those languages.  I will 
use single-quotes where required to enclose a string containing double-quotes,
and I may also use them for other reasons (for example if I am re-using 
a snippet of code copied from a Stack Overflow answer or other outside 
source).  Where a group of string constants appear together (e.g. in 
an array or as keys, or values in a dictionary structure), and some
strings need single-quotes and others don't, I will use my own judgement
to decide whether to prefer double-quotes where single-quotes are not 
required or whether to be consistent across the structure.

PEP-8 mandates that strings surrounded by 3 quote characters should always
use double-quotes, that mandate will be enforced.

At the time of writing, requirements.txt makes both pycodestyle and flake8 
available for style enforcement.  A decision will be made at some later
time in relation to whether one of these or some other tool is used as 
the primary enforcement method.

Credits
-------

The directory layout for this project is based on the 'samplemod' sample module project discussed by Kenneth Reitz.

`Learn more <https://kennethreitz.org/essays/2013-01-repository_structure_and_python>`_.
