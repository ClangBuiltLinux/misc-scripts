# CBL/reduce
A family of scripts to prepare and execute reduction (cvise, llvm-reduce) workflows.

Currently, there are two scripts:

1) prep
> Prepare a target file for reduction (see Basic Usage)

2) flags
> Minimize the compiler flags required to reproduce behavior. Use after prep

## Dependencies
* Python 3.11
* [icecream](https://pypi.org/project/icecream/)
* [C-Vise](https://github.com/marxin/cvise)

## Basic Usage

`$ python reduce.py -h`

### prep
> Get help with prep

`$ python reduce.py prep -h`

> Prepare lib/string for reduction by producing a
> `string.i`, `test.sh` and a `flags.txt` in a temporary directory which are
> ready-for-consumption by tools like `cvise` and `llvm-reduce`

`$ python reduce.py prep lib/string -p /path/to/linux -o $(mktemp -d)`

> Or, try providing a custom build command
>
`$ reduce prep -p $LINUX -o $(mktemp -d) -- make -j8 LLVM=1 V=1 lib/string`



### flags
> Get help with flags

`$ python reduce.py flags -h`

> After running `prep`, reduce flags.txt

`$ python reduce.py flags`

> **Note**
> Change your cwd to wherever `flags.txt` is located or try the `-p` option.



## Contributions
Author: Justin Stitt <justinstitt@google.com>

Suggested-by: Nick Desaulniers <ndesaulniers@google.com>
