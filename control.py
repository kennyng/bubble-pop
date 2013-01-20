#! /usr/bin/env python

import cv

ESC_KEY = 27

def WaitKey(delay = 0):
    code = cv.WaitKey(delay)
    if code == -1:
        key = -1
    else:
        key = code & ~0b100000000000000000000

    return key

if __name__ == '__main__':
    cv.NamedWindow("gamescreen", cv.CV_WINDOW_AUTOSIZE)
    cv.ShowImage("gamescreen", None)
    code = cv.WaitKey()
    
    print "%d - %d" %(code & ~0b100000000000000000000, code)
