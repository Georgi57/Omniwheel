import cv,threading,time

class FrameBufferThread(threading.Thread):
    """This is a thread that grabs a camera image from the buffer"""
    running=True
    def run(self):
        global _camera, lock
        while self.running:
            """
            I'm using a lock to use the resource uninterrupted.
            Currently variable, where camera image is saved, can be called in two threads,
            which can make one of them crash.
            Lock is the simplest way of avoiding crashing when using a shared resource
            """
            lock.acquire()
            try:
                cv.GrabFrame(_camera)
                print "Frame grabbed"
            finally:
                lock.release()

    def stop(self):
        """Used to stop the thread"""
        self.running=False

"""Initializing the camera and a lock"""
global _camera, lock
_camera = cv.CreateCameraCapture(0)
lock=threading.RLock()

"""Starting the thread"""
_camera_polling_thread = FrameBufferThread()
_camera_polling_thread.start()

t=time.time()
cv.NamedWindow( "Camera", cv.CV_WINDOW_AUTOSIZE )

while 1:
    """Main thread"""
    t=time.time()
    lock.acquire()
    try:
        """Getting the image"""
        img = cv.RetrieveFrame(_camera)
        print time.time()-t," time spent on retrieving the frame"
    finally:
        lock.release()
    cv.ShowImage( "Camera", img )
    if cv.WaitKey(1) == 27:
        break

"""Disabling the thread and closing the window"""
_camera_polling_thread.stop()
cv.DestroyAllWindows()
