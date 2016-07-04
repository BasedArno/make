#!/usr/bin/env python3
#
# Make(.py) - object oriented build automation software in the spirit of make
#
# created by: Arno Sebastian Byrd
#

import getopt
import importlib
import inspect
import hashlib
import os
import subprocess
import sys

__all__ = ["run", "rule", "Rule", "__default__"]

## utility functions for make.py build files
def flatten(*xs):
    """ Recursively iterate lists and tuples. """
    flat_list = []
    for x in xs:
        if isinstance(x, (list, tuple)):
            for y in flatten(*x):
                flat_list.append(y)
        else:
            flat_list.append(x)
    return flat_list

def run(*args, **kwargs):
    """ Run passes all arguments to subprocess.Popen """
    args = flatten(*args)
    print("running")
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    return
## ------

## imported rule definitions
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

# rule class wrapper for function
class Rule(object):
    __all__ = set()
    def __init__(self, fn):
        self.__class__.__all__.add(self) # for finding all instances later
        self.fn = fn
        self.targets = []
        self.sources = []
        self.node = "singleton"
    def __call__(self,  *args, **kwargs):
        self.fn(*args, **kwargs)
    def add_relation(self, targets, sources):
        # check to see if targets was a single string
        if type(targets) == str:
            self.targets = [targets]
        else:
            self.targets = targets

        # check to see if sources was a single string
        if type(sources) == str:
            self.sources = [sources]
        else:
            self.sources = sources

        # classify the node type
        if len(self.targets) == 0 and len(self.sources) == 0:
            self.node = "singleton"
        elif len(self.targets) == 1 and len(self.sources) == 0:
            self.node = "root"
        elif len(self.targets) == 1 and len(self.sources) == 1:
            self.node = "branch"
        elif len(self.targets) == 1 and len(self.sources) > 1:
            self.node = "fork"
        elif len(self.targets) == len(self.sources):
            self.node = "kbranch"
        else:
            raise Error()
    def rule_name(self):
        return self.fn.__name__

# rule with targets and sources - wrapper for class defn
def rule(targets = [], sources = []):
    """ Decorator for job functions. """
    def make_rule_class(fn):
        fn = Rule(fn)
        fn.add_relation(targets, sources)
    return make_rule_class

# the default rule to execute
__default__ = "build"
## ------

##
## ------

## make magic
def get_hash(file):
    """ Evaluate md5 checksum of file. """
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    md5 = hashlib.md5()
    with open(file, 'rb') as file:
        while True:
            data = file.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

def execute(job):
    # check to make sure all sources have been built
    if job.node == "singleton":
        job()
    elif job.node == "root":
        job()
    elif job.node == "branch":
        for source in job.sources:
            for other_job in job.__all__:
                if source == other_job.rule_name():
                    execute(other_job)
                    job()
                    break
    elif job.node == "fork":
        for source in job.sources:
            for other_job in job.__all__:
                if source == other_job.rule_name():
                    execute(other_job)
        job()
    elif job.node == "kbranch":
        for source in job.sources:
            for other_job in job.__all__:
                if source == other_job.rule_name():
                    execute(other_job)
        for idx in range(len(job.targets)):
            job(job.targets[idx], job.sources[idx])

def main(file_name = 'build.py', debug_mode = True, *targets):
    """
    """
    # import build module
    if file_name.endswith(".py"):
        print("filename =", file_name)
        module_name = file_name[:-3]
        pathtofile = os.path.join(os.getcwd(), file_name)
        module = importlib.machinery.SourceFileLoader(module_name,
                pathtofile).load_module()
        #module = importlib.import_module(module_name)
        debug_mode and print("module loaded")
    else:
        print("File given not valid build file. Must end in '.py'")
        sys.exit(2)

    # execute rules associated with targets
    if len(targets) == 0:
        targets = (__default__,) # default target
    debug_mode and print("Targets are", targets)
    for job in module.Rule.__all__:
        for target in targets:
            if job.rule_name() == target:
                debug_mode and print("* Executing: ", job.rule_name())
                execute(job)
## ------

## if called as executable
def usage():
    print('make.py - a pythonic automation program in the spirit of make')
    print('\nUsage: make.py [options] rule(s)\n')
    print('Version 0.0.1')

if __name__ == "__main__":
    # defaults
    file_name = "build.py"
    debug_mode = False

    # parse the options passed
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdb:", ["help", "debug-mode", "build-file="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-d', '--debug-mode'):
            debug_mode = True
        elif opt in ('-b', '--build-file'):
            print("-", file_name)
            file_name = arg
        else:
            assert False, "unhandled option"

    # GO #
    debug_mode and print("* Calling main with:")
    debug_mode and print("file_name = ", file_name)
    debug_mode and print("debug_mode = ", debug_mode)
    debug_mode and print("args = ", args)
    main(file_name, debug_mode, *args)
## ------
