import time
class FilghtController(object):
    """docstring for FilghtController."""
    def __init__(self, board, emitter):
        super(FilghtController, self).__init__()
        self.board = board
        self.board.getData(self.board.RC)
        self.emitter = emitter
        self.rc = self.toRawRc(self.board.rcChannels)
        self.last = self.board.rcChannels["timestamp"]
        self.info = {}
    def run(self):
        while True:
            # just blast every second the rc channels
            #this emulates the behaviour of a flight controller
            self.sendRc(self.rc)
            self.getInfo()
            time.sleep(.5)
    def toRawRc(self,d):
        data = []
        data[0] = d["roll"]
        data[1] = d["pitch"]
        data[2] = d["yaw"]
        data[3] = d["throttle"]
        data[4] = 1000
        data[5] = 1040
        data[6] = 1000
        data[7] = 1000
        return data
    def sendRc(self,in_):
        self.rc = in_
        try:
            self.board.sendCMDreceiveATT(16, self.board.SET_RAW_RC, self.toRawRc(in_))
        except Exception as e:
            print(e)
        return data
    def getInfo(self):
        ret = {}
        self.board.sendCMD(self.board.ATTITUDE)
        self.board.sendCMD(self.board.ALTITUDE)

        ret["attitude"] = self.board.attitude
        ret["altitude"] = self.board.altitude
        self.emitter.emit("info", ret)
        self.info = ret
        return ret
