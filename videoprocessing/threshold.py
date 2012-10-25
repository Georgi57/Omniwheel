import cv,cv2

#Camera
cam = cv.CreateCameraCapture(0)
objects = "Ball/Blue gate/Yellow gate/Green/Black/White"
colors = []

def save_changes(idx):
    # Save changes made in the sliders
    obj = cv.GetTrackbarPos('object', objects)
    hue = cv.GetTrackbarPos('hue', objects)
    saturation = cv.GetTrackbarPos('saturation', objects)
    value = cv.GetTrackbarPos('value', objects)
    xhue = cv.GetTrackbarPos('maxhue', objects)
    xsaturation = cv.GetTrackbarPos('maxsaturation', objects)
    xvalue = cv.GetTrackbarPos('maxvalue', objects)
    
    currentcolors=[hue,saturation,value,xhue,xsaturation,xvalue]
    colors[obj*6:(obj+1)*6]=currentcolors[:]
    
    string=""
    for i in colors:
        string+=str(i)+" "
    f = open('thresholdvalues.txt',  'w')
    f.write(string)
    f.close()

def change_object(idx):
    currentcolors = []
    for i in range(6):
        currentcolors.append(colors[idx*6+i])
    cv.SetTrackbarPos('object', objects, idx)
    cv.SetTrackbarPos('hue', objects, int(currentcolors[0]))
    cv.SetTrackbarPos('saturation', objects, int(currentcolors[1]))
    cv.SetTrackbarPos('value', objects, int(currentcolors[2]))
    cv.SetTrackbarPos('maxhue', objects, int(currentcolors[3]))
    cv.SetTrackbarPos('maxsaturation', objects, int(currentcolors[4]))
    cv.SetTrackbarPos('maxvalue', objects, int(currentcolors[5]))

#Create for the occasion, when there are no file
for i in range(36):
    if i%6>=0 and i%6<3:
        colors.append(0)
    else:
        colors.append(255)
try:
    f = open('thresholdvalues.txt',  'r')
    a = f.read()
    c=a.split()
    if len(c)==len(colors):
        colors=c
    f.close()
    print "Colors:"
except:
    print "There was no file. Creating new values:"

currentcolors = []
for i in range(6):
    currentcolors.append(colors[0*6+i])
print colors

#Interface
cv.NamedWindow("webcam", cv.CV_WINDOW_AUTOSIZE)
cv.NamedWindow("Thresholded", cv.CV_WINDOW_AUTOSIZE)
cv.NamedWindow(objects, cv.CV_WINDOW_NORMAL)
cv.MoveWindow('webcam', 640, 0)
cv.CreateTrackbar('object', objects,  0,  5, change_object)
cv.CreateTrackbar('hue', objects,  int(currentcolors[0]),  255, save_changes)
cv.CreateTrackbar('saturation', objects,  int(currentcolors[1]),  255,  save_changes)
cv.CreateTrackbar('value', objects,  int(currentcolors[2]),  255,  save_changes)
cv.CreateTrackbar('maxhue', objects,  int(currentcolors[3]),  255,  save_changes)
cv.CreateTrackbar('maxsaturation', objects, int(currentcolors[4]),  255,  save_changes)
cv.CreateTrackbar('maxvalue', objects,  int(currentcolors[5]),  255,  save_changes)

change_object(0)
while True:
    #Get camera frame
    frame = cv.QueryFrame(cam)

    obj = cv.GetTrackbarPos('object', objects)
    currentcolors = []
    for i in range(6):
        currentcolors.append(int(colors[obj*6+i]))
    
    hsv_frame = cv.CreateImage(cv.GetSize(frame), 8, 3) 
    cv.CvtColor(frame, hsv_frame, cv.CV_BGR2HSV) 
    thresholded_frame =  cv.CreateImage(cv.GetSize(hsv_frame), 8, 1)  
    cv.InRangeS(hsv_frame, (currentcolors[0], currentcolors[1], currentcolors[2]), (currentcolors[3], currentcolors[4], currentcolors[5]), thresholded_frame) 
    cv.Smooth(thresholded_frame, thresholded_frame, cv.CV_BLUR, 3);
    
    cv.ShowImage("webcam", frame)
    cv.ShowImage("Thresholded",  thresholded_frame)
    
    key=cv.WaitKey(100)
    if key == 27:
        break

cv.DestroyAllWindows()
