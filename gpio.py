#!/usr/bin/env python

import io 

#gpioTuple = (15, 14, 13, 12, 36, 37, 38, 39)

gpioValue = {'high': 1, 'low': 0}

NONE    = 'none'
RISING  = 'rising'
FALLING = 'falling'
BOTH    = 'both'

def gpioExport(gpioIndex):
    with open('/sys/class/gpio/export', 'wb') as f:
        f.write(str(gpioIndex).encode())

def gpioUnexport(gpioIndex):
    with open('/sys/class/gpio/unexport', 'wb') as f:
        f.write(str(gpioIndex).encode())

def setInput(gpioIndex):
    with open('/sys/class/gpio/gpio%d/direction' % gpioIndex, 'wb') as f:
        f.write('in'.encode())

def setOutput(gpioIndex):
    with open('/sys/class/gpio/gpio%d/direction' % gpioIndex, 'wb') as f:
        f.write('out'.encode())

def getInputValue(gpioIndex):
    with open('/sys/class/gpio/gpio%d/value' % gpioIndex, 'r+') as f:
        return f.read().strip('\n')  # delete the '\n' 

def setOutputValue(gpioIndex, value):
    with open('/sys/class/gpio/gpio%d/value' % gpioIndex, 'wb') as f:
        return f.write(str(value).encode())

def setEdge(gpioIndex, edge):
    with open('/sys/class/gpio/gpio%d/edge' % gpioIndex, 'wb') as f:
        f.write(edge.encode())

def getEdge(gpioIndex):
    with open('/sys/class/gpio/gpio%d/edge' % gpioIndex, 'r+') as f:
        return f.read().strip('\n')

def getGpioValue(gpioIndex):
    gpioExport(gpioIndex)
    setInput(gpioIndex)
    val = getInputValue(gpioIndex)
    gpioUnexport(gpioIndex)
    return val

def getGpioValues(gpioTuple):
    gpioValues = []
    for i in gpioTuple:
        gpioExport(i)
        setInput(i)
        gpioValues.append(getInputValue(i))
        gpioUnexport(i)
    return gpioValues

def waitForEdge(gpioIndex):
    pass
