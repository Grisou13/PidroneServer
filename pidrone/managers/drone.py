import MultiWii from pyMultiWii
import threading


board = MultiWii("/dev/ttyUSB0")


class AttitudeThread(Thread):
    def __init__(self, multiwii, emiter):
        Thread.__init__(self)
        self.drone = multiwii
        self.emiter = emiter
    def run(self):
        while True:
            try:
                self.drone.getData(MultiWii.ATTITUDE)
                self.emiter.emit("drone_info", data = board.attitude)
                # TODO send attitude to socket.io
            except Exception,error:
                print("Error on AttitudeThread: "+str(error))
            time.sleep(.5)


def run():
    t = AttitudeThread()
    t.run()
    t.join()
