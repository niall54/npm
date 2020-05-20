"""
This file has all the code required for saving/loading the parameters of a txt
file from/to a python structure for subsequent use
"""

def struct2txt(struct,filename):
    """
    This function takes a python structure, struct, and saves its parameters
    in a txt file located at a position given by filename.
    Does include:
        - automatic generation of directory, filename must be 
          'dir1/dir2/file.txt'
    Does NOT include:
        - variable type saving
    """
    import os
    import errno
    
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
                
    with open(filename, "w") as f:
        for key, value in struct.items():
            f.write("{}: {}\n".format(key,value))
    
def txt2struct(filename):
    """
    This function takes a filename, and returns a structure of 
    Does NOT include:
        - automatic setting of variable type
    """
    struct = {}
    with open(filename,"r") as f:
        for i in f:
            key, val = i.split("\n")[0].split(":")
            struct[key] = val
    return struct


if __name__ =='__main__':
    struct = {'this':'working'}
    filename = 'params/wgm_resonator_sim/test.txt'
    struct2txt(struct,filename)
