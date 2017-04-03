def remap( x, oMin, oMax, nMin, nMax ):

    #range check
    if oMin == oMax:
        print("Warning: Zero input range")
        return None

    if nMin == nMax:
        print("Warning: Zero output range")
        return None

    #check reversed input range
    reverseInput = False
    oldMin = min( oMin, oMax )
    oldMax = max( oMin, oMax )
    if not oldMin == oMin:
        reverseInput = True

    #check reversed output range
    reverseOutput = False
    newMin = min( nMin, nMax )
    newMax = max( nMin, nMax )
    if not newMin == nMin :
        reverseOutput = True

    portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
    if reverseInput:
        portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return result
def toRawRc(d):
    data = []
    #TODO map with minthrottle, maxthrottle value and nothing hard codded
    # data[0] = remap(d["roll"],0,100,1000,2000)
    # data[1] = remap(d["pitch"],0,100,1000,2000)
    # data[2] = remap(d["yaw"],0,100,1000,2000)
    # data[3] = remap(d["throttle"],0,100,1100,2000)
    data[0] = d["roll"]
    data[1] = d["pitch"]
    data[2] = d["yaw"]
    data[3] = d["throttle"]
    data[4] = 1000
    data[5] = 1040
    data[6] = 1000
    data[7] = 1000
    return data

def sendRc(in_):
    try:
        board.sendCMD(16, board.SET_RAW_RC, toRawRc(in_))
    except Exception as e:
        print(e)
    return board.getData(board.RC)
