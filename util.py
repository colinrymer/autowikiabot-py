### File borrowed from Zack Maril @ https://github.com/zmaril
import re, time

def formatted(*args):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    return "["+now+"] "+" ".join(map(str,args))


def log(*args):
    print(formatted(args))

def fail(*args):
    print('\033[91m'+formatted(args)+'\033[0m')

def warn(*args):
    print('\033[93m'+formatted(args)+'\033[0m')

def success(*args):
    print('\033[92m'+formatted(args)+'\033[0m')
    
def special(*args):
    print('\033[95m'+formatted(args)+'\033[0m')
    
def bluelog(*args):
    print('\033[94m'+formatted(args)+'\033[0m')
