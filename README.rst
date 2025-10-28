moonshine-wrangler
==================

Based on the 'samplemod' sample module project discussed by Kenneth Reitz.

`Learn more <https://kennethreitz.org/essays/2013-01-repository_structure_and_python>`_.

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
  Lines up to 140 characters will be tolerated if the maintainer considers that 
  a single long line is considered more readable than multiple lines of 100 
  characters or less.

At the time of writing, requirements.txt makes both pycodestyle and flake8 
available for style enforcement.  A decision will be made at some later
time in relation to whether one of these or some other tool is used as 
the primary enforcement method.



