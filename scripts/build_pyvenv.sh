#!/bin/sh

osname=$(uname -a | grep -e Ubuntu -e Debian -e Darwin -o | uniq)
echo osname=$osname

# We might need CPU architecture - if so get it like this
# cpuarch=$(uname -a | grep -e "x86_64" -e "aarch64" -o | uniq)
# echo cpuarch=$cpuarch

# If we are already in a Python virtual environment deactivate it
if [ ! -z "$(which deactivate)" ]
then
    deactivate
fi

if [ "$osname" = "Ubuntu" ] || [ "$osname" = "Debian" ] 
then
    sudo apt-get install python3-pyaudio portaudio19-dev 
elif [ "$osname" = "Darwin" ]
then
    # on macOS, this script will only work if the following
    # conditions are satisfied:
    # + macports infrastructure must be installed
    # + python invokes macports Python version 3.10
    port_path=
    python_path=
    python_version=
    if [ ! -x "$(which port)" ]
    then
        echo No 'port' executable found
        echo install from:
        echo + https://github.com/macports/macports-base/releases/download/v2.12.6/MacPorts-2.12.6-10.15-Catalina.pkg
        echo + https://github.com/macports/macports-base/releases/download/v2.12.6/MacPorts-2.12.6-15-Sequoia.pkg
        echo + or a suitable version for your operating system version.
        exit 51
    elif [ ! "$(which python)" = "/opt/local/bin/python" ]
    then
        echo Python not found in expected location
        echo Please ensure that python is the version provided by macports.org 
        echo which is expected to be at /opt/local/bin/python
        exit 52
    elif [ ! "$(python --version)" = "Python 3.10.21" ]
    then
        echo Python version installed does not match expected version.
        echo Python 3.10.X is required so that macports package py310-pyaudio will work
        echo If X!=21, please update the expected version in build_pyvenv.sh
        exit 53
    else
        sudo port install py310-pyaudio 
        export CPPFLAGS="-I/opt/local/include"
        export LDFLAGS="-L/opt/local/lib"
    fi
fi
# If we get this far, all expectations for the OS detected are satisfied

pyvenv_dir=_work/.pyvenv

if [ "$1" = "--clean" ]
then
    rm -rf $pyvenv_dir
fi
python -m venv $pyvenv_dir
. $pyvenv_dir/bin/activate
python -m pip install mido python-rtmidi tinysoundfont requests pysqlite3 



