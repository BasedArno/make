# make.py
An object oriented build automation software in the spirit of make.

## Description
Make.py is intended to copy as many of the good things about make while fixing
as much of the bad stuff as possible. Make.py uses the rule based instructions
from make but implemented in python instead of make. This automatically removes
many of the basic problems with make - namely that it's an underpowered
programming language that few people know. You can use the if statements, for
loops, and regexes that you know and love. There are no more wonky tab issues
(unless you still use these from python). Phony targets are a thing of the past
too.

Additionally make.py will (once completed) provide many benefits over make.
Make.py will use checksums instead of file modification times. Make.py will
also include the option for parallel builds. It will eventually include the
possibility of capturing output to separate files for separate rules.

Long term goals for the project will include lots of utility functions for
common build tasks. I also want the ability to output dependency graphs.

## Installation
Make.py can go anywhere on the path. I usually put it in $HOME/bin. Python must
also be made aware of the file's location. If it's in the same directory as
your build file you don't need to do anything. If not you can add:

```python
import sys
sys.path.append("/path/to/dir/with/make.py")
import make
```

at the start of your build file, or this can be done more permanently with:

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/dir/with/make.py"
```

## Usage
The default build file will be assumed to be 'build.py'. If using a different
file designate it with the '-f' flag. Use the rule decorator above every
function you want as a task. The two possible inputs to the rule decarator are
the targets and the sources (dependencies + libraries as inputs to be added
later). Example build file included below.

```python
from make import *

# Variables
cc = 'g++'
cflags = ['-Wall', '-std=c++11', '-o']
exe = 'hello'
src = 'hello.cxx'

# Rules
@rule(exe, src)
def build():
    print("compiling")
    proc = run([cc, cflags, exe, src])

@rule()
def clean():
    print("cleaning")
    proc = run(["rm", exe])
```

To run use the command:

```bash
make.py [rules]
```

Other examples include:

```bash
make.py -f setup.py
make.py configure build install
make.py --debug-mode
```

and so on.

## Comments
Email any comments or questions to me (Arno) at mindlessentropy@gmail.com
