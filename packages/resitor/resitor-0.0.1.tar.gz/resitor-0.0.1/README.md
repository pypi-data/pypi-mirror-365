# resitor

- HomePage: https://github.com/kzhu2099/Resource-Monitor
- Issues: https://github.com/kzhu2099/Resource-Monitor/issues

[![PyPI Downloads](https://static.pepy.tech/badge/resitor)](https://pepy.tech/projects/resitor)

Author: Kevin Zhu

## Features

- graphical per-process monitoring of CPU and memory
- last-frame saving
- customization
- multiple PIDs
- CLI or Python

## Installation

To install resitor, use pip: ```pip install resitor```.

However, many prefer to use a virtual environment.

macOS / Linux:

```sh
# make your desired directory
mkdir /path/to/your/directory
cd /path/to/your/directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install resitor
source .venv/bin/activate
pip install resitor

deactivate # when you are completely done
```

Windows CMD:

```sh
# make your desired directory
mkdir C:path\to\your\directory
cd C:path\to\your\directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install resitor
.venv\Scripts\activate
pip install resitor

deactivate # when you are completely done
```

## Usage

First, start a process (a python script). In the `Tests/` folder, there is an existing `long_program.py` (be careful, it takes resources so you must manually end it when you are done).

It will print the `PID` of that process, through `os.getpid()`. Then, use `python3 -m resitor <pid>` to monitor the resource usage.

Or, you may use the `start_monitor(<pid>, ...)` function and input your desired parameters.

You may enter a list of `PIDs` through `python3 -m resitor <pid1> <pid2> ...`. A list of PIDs can be inputed to `start_monitor()` as well.

If you don't want to watch CPU or memory, simply add the `-noc` or `nom` flags.

For Windows / Linux users, you may also watch the disk usage through the `-dsk` flag.

Currently, `psutil` (what this is built on) does not have per-process network monitoring. Furthermore, macOS users do not have access to per-process disk monitoring.

## License

The License is an MIT License found in the LICENSE file.