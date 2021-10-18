'''
Written by Timothey Lemley for Mohawk Industries
September 29, 2021
released as open source
'''
import numpy

def get_bit(variable,index):
    return ((variable&(1<<index))!=0)

def set_bit(variable, index):
    return variable | (1<<index)
def clear_bit(variable, index):
    return variable & ~(1<<index)

def write_bit(variable, index, status):
    if status == True:
        return set_bit(variable, index)
    else:
        return clear_bit(variable,index)

def get_words(value, resolution=2):
    int_value = int(value*(10**resolution))
    upper = numpy.array([int_value>>16], dtype="uint16")[0]
    lower = numpy.array([int_value], dtype="uint16")[0]
    return upper, lower

def get_float(upper, lower, resolution=2):
    value = (upper<<16)+lower
    return float(value/(10**resolution))

def bp(variable, digits=16, resolution=0):
    string = ""
    for i in range(digits):
        string = string + str ( int( get_bit( int( variable*(10**resolution) ), ( (digits-1)-i ) ) ) )
    return string