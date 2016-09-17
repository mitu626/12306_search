a='''
12306 tickets info query via command-line.

Usage:
    test <from> <to> <date>

Options:
    -h,--help show help menu

Examples:
    main beijing datong 2016-08-25
'''
from docopt import docopt
arguments=docopt(a)
print arguments