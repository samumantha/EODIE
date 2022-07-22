#!/usr/bin/env python
from eodie.userinput import UserInput
from eodie.validator import Validator
from eodie.workflow import Workflow

def read_userinput():
    """Read and validate userinputs.

    Returns:
    --------
    userinput: class Userinput
        validated Userinputs
    """
    userinput = UserInput()      
    Validator(userinput)
    return userinput   

def main():    
    """Fetch userinput and launch workflow."""
    userinput = read_userinput()  
    Workflow(userinput)   
    
if __name__ == '__main__':
    main()