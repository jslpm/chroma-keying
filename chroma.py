import cv2
import numpy as np

def setColor(action, x, y, flags, userdata):
    global points
    global isColor
    global pixelColorHSV
    global frame
    global frameHSV
    
    if action == cv2.EVENT_LBUTTONDOWN and isColor == False:
        isColor = True
        points = (x,y)
        pixelColorHSV = tuple(frameHSV[y,x,:])
        
        newImage = removeBackground()
        newImage = addAnnotation(newImage)
        cv2.imshow(windowName, newImage)


def removeBackground():
    global trackTolerance
    global trackSoftness
    global trackDefringe
    global pixelColorHSV
    global isBackground
    global frame
    global frameHSV
    
    # modify brightness of green channel (Defringe)
    
    # split BGR channels
    B,G,R = cv2.split(frame)
    
    # change brightness in green channel
    brightnessOffset = 2*trackDefringe - 100
    gModified = np.uint8(np.clip((np.int32(G) + np.ones_like(G, dtype="int32")*brightnessOffset), 0, 255))
    
    # merge modified frame
    frameModified = cv2.merge((B,gModified,R))
    
    # convert modified frame to HSV color space
    frameModifiedHSV = cv2.cvtColor(frameModified, cv2.COLOR_BGR2HSV)
        
    # split HSV channels
    h,s,v = cv2.split(frameHSV)
    hMod,sMod,vMod = cv2.split(frameModifiedHSV)
    
    # remove color background in the Hue channel (Tolerance)
    
    # select color ranges
    colorValue = pixelColorHSV[0]
    upperH = np.array(np.clip(colorValue +  trackTolerance, 0, 180), dtype="uint8")
    lowerH = np.array(np.clip(colorValue - trackTolerance, 0, 180), dtype="uint8")
    
    mask = cv2.inRange(hMod, lowerH, upperH)
    
    # invert color mask
    mask = 255-mask    
        
    # blur the mask (Softness)
        
    if trackSoftness > 0:
        maskBlur = cv2.blur(mask, (10*trackSoftness,10*trackSoftness), (-1,-1))
        maskBlur = np.uint8(np.round((maskBlur/255.0)*(mask/255.0)*255))
    else:
        maskBlur = mask
    
    # apply mask to Value channel
    newV = np.uint8(np.round((v/255.0*maskBlur/255.0)*255))
    
    # merge image without background
    imageWithoutBg = cv2.merge((h,s,newV))
    
    # convert to BGR for displaying
    imageWithoutBg = cv2.cvtColor(imageWithoutBg, cv2.COLOR_HSV2BGR)
    
    # Add background
    
    # check if trackbar for background is activated
    if isBackground == True:
        
        # invert mask
        maskInv = 255 - mask
    
        # create mask with 3 channels
        maskInv3Ch = np.ones_like(bg)
        for i in range(3):
            maskInv3Ch[:,:,i] = maskInv
        
        # apply inverted mask to background
        bgCut = np.uint8(np.round((bg/255.0)*(maskInv3Ch/255.0)*255))
        
        # combine background and image
        imageWithNewBg = cv2.add(imageWithoutBg, bgCut)
    
        output = imageWithNewBg
        
    else:
        
        output = imageWithoutBg
    
    return output


def getTolerance(*args):
    global trackTolerance
    global frame
    global frameHSV
    
    trackTolerance = cv2.getTrackbarPos("Tolerance", windowName)
    
    if isColor == True:
        newImage = removeBackground()
        newImage = addAnnotation(newImage)
        cv2.imshow(windowName, newImage)


def getSoftness(*args):
    global trackSoftness
    global frame
    global frameHSV
    
    trackSoftness = cv2.getTrackbarPos("Softness", windowName)
    
    if isColor == True:
        newImage = removeBackground()
        newImage = addAnnotation(newImage)
        cv2.imshow(windowName, newImage)


def getDefringe(*args):
    global trackDefringe
    global frame
    global frameHSV
    
    trackDefringe = cv2.getTrackbarPos("Defringe", windowName)
    
    if isColor == True:
        newImage = removeBackground()
        newImage = addAnnotation(newImage)
        cv2.imshow(windowName, newImage)


def updateFrame(*args):
    global frame
    global frameHSV    
    
    framePos = cv2.getTrackbarPos("Frame", windowName)
    ret = cap.set(cv2.CAP_PROP_POS_FRAMES,framePos)

    # read frame
    ret, frame = cap.read()
    
    # convert frame to HSV color space
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    if isColor == True:
        newImage = removeBackground()
    else:
        newImage = frame
    
    newImage = addAnnotation(newImage)
    cv2.imshow(windowName, newImage)


def activateBackground(*args):
    global isBackground
    global frame
    global frameHSV
    
    trackBg = cv2.getTrackbarPos("Background", windowName)
    
    if isColor == True:
        if trackBg == 0:
            isBackground = False
        else:
            isBackground = True
        newImage = removeBackground()
        newImage = addAnnotation(newImage)
        cv2.imshow(windowName, newImage)


def addAnnotation(image):
    
    # annotations
    imageCopied = image.copy()  # frame for displaying
    cv2.putText(imageCopied, "Click to remove green scene", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 4)
    cv2.putText(imageCopied, "esc: exit", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 4)
    cv2.putText(imageCopied, "s: save video", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 4)
    
    return imageCopied


def addAnnotationWriter(image):
    
    # annotations
    imageCopied = image.copy()  # frame for displaying
    cv2.putText(imageCopied, "VideoWriter running...", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 4)
    cv2.putText(imageCopied, "a: abort", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 4)
    
    return imageCopied


def addAnnotationAborted(image):
    
    # annotations
    imageCopied = image.copy()  # frame for displaying
    cv2.putText(imageCopied, "a: VideoWriter aborted", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 4)
    
    return imageCopied


def addAnnotationFinished(image):
    
    # annotations
    imageCopied = image.copy()  # frame for displaying
    cv2.putText(imageCopied, "VideoWriter finished", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 4)
    
    return imageCopied


# global variables
points = []
frame = []
frameHSV = []
trackTolerance = 0
trackSoftness = 0
trackDefringe = 50
isColor = False
isBackground = False

# read video
cap = cv2.VideoCapture("greenscreen-asteroid.mp4")

# check for video
if (cap.isOpened() == False):
    print("Error opening video!")
else:
    print("Video loaded succesfully!")
    
# read background
bg = cv2.imread("space.jpg", cv2.IMREAD_COLOR)

# check for background
if bg is None:
    print("Error opening background!")
else:
    print("Background loaded succesfully!")

# read frame
ret, frame = cap.read()     # frame for procesing
frameCopied = addAnnotation(frame)

# get number of frames
minCapNumber = 0
maxCapNumber = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1

# get frame height and width
frameHeight, frameWidth = frame.shape[:2]

# create window
windowName = "Display Frame"
cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
cv2.imshow(windowName, frameCopied)
cv2.resizeWindow(windowName, frameWidth, frameHeight)

# convert frame to HSV color space
frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# mouse callback to select color
cv2.setMouseCallback(windowName, setColor)

# trackbars for: tolerance, softness and defringe
cv2.createTrackbar("Frame", windowName, minCapNumber, maxCapNumber, updateFrame)
cv2.createTrackbar("Tolerance",windowName, 0, 100, getTolerance)
cv2.createTrackbar("Softness",windowName, 0, 100, getSoftness)
cv2.createTrackbar("Defringe",windowName, 50, 100, getDefringe)
cv2.createTrackbar("Background",windowName, 0, 1, activateBackground)

# wait for keyboard
k = 0
while k != 27:
    
    k = cv2.waitKey(20) & 0xFF
    
    # save video
    if k == ord('s'):
        # create video object
        fps = round(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        numberFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        ret = cap.set(cv2.CAP_PROP_POS_FRAMES,0)
        out = cv2.VideoWriter("newVideo.mp4", cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width,frame_height))
        
        print("VideoWriter started")
        
        while(cap.isOpened()):
            #capture frame-by-frame
            ret, frame = cap.read()
            if ret == True:
                frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                frameBg = removeBackground()
                # write the frame into the file
                out.write(frameBg)
                # wait for 10ms before moving on to the next frame
                frameBg = addAnnotationWriter(frameBg)
                cv2.imshow(windowName, frameBg)
                k = cv2.waitKey(10)
                if k == ord('a'):
                    frameBg = removeBackground()
                    frameBg = addAnnotationAborted(frameBg)
                    cv2.imshow(windowName, frameBg)
                    print("VideoWriter aborted")
                    break
            # break the loop
            else:
                break
        frameBg = removeBackground()
        frameBg = addAnnotationFinished(frameBg)
        cv2.imshow(windowName, frameBg)        
        print("VideoWriter finished")
        out.release()
        
        
# close program
cap.release()
cv2.destroyAllWindows()
