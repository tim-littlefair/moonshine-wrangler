#! /bin/sh

# Check that the correct Python virtual environment has been activated
if [ "$(which python)" != "$(pwd)/_work/.pyvenv/bin/python" ]
then
    echo Python virtual environment for sandbox not found.
    echo This script must be run from the root directory of the sandbox and
    echo must be running after activating a Python venv at ./_work/.pyvenv.
    exit 91
fi

if [ "$1" = "--clean" ]
then
    cd _work
    rm -rf reference_files  fuse_data tone_lt_data tone_mobile_data
    cd ..
fi

time python moonshinewrangler/_get_working_resources.py

if [ -d ./_work/fuse_data ]
then
    echo Using previously populated fuse_data
else
    time python moonshinewrangler/process_fuse_installer.py
fi

if [ -d ./_work/tone_lt_data ]
then
    echo Using previously populated tone_lt_data
else
    time python moonshinewrangler/process_tone_lt_installer.py
fi

if [ -d ./_work/tone_mobile_data ]
then
    echo Using previously populated tone_mobile_data
else
    time python moonshinewrangler/process_tone_mobile_xapk.py
fi





