 #!/usr/bin/env python
    # opencv-find-face : Opencv face tracking with pan/tilt search and lock
    # written by Claude Pageau -
    # This is a little laggy but does work OK.
    # Uses pipan.py module from openelectrons.com RPI camera pan/tilt to control
    # camera tracking or use your own pan/tilt module and modify code accordingly.
    # if you are not using openelectrons.com pan/tilt hardware.
    # Also picamera python module must be installed as well as opencv
    # To install opencv and python for opencv
    # sudo apt-get install libopencv-dev python-opencv
    # To install picamera python module
    # sudo apt-get install python-picamera
    # You will also need to install python picamera.array tha includes numpy
    # sudo pip install "picamera[array]"
    # copy /usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml
    # to same folder that this python script is in.
    #    Note
    # v4l2 driver is not used since stream is created using picamera module
    # using picamera.array
    # If you have any questions email pageauc@gmail.com

    import io
    import time
    import picamera
    import picamera.array
    import cv2
    # openelectron.com python module and files from the OpenElectron RPI camera pan/tilt
    # Copy pipan.py to same folder as this script.
    import pipan

    p = pipan.PiPan()

    # Approx Center of Pan/Tilt motion
    pan_x_c = 150
    pan_y_c = 140

    # bounds checking for pan/tilt search.
    limit_y_bottom = 90
    limit_y_top = 150
    limit_y_level = 140
    limit_x_left = 60
    limit_x_right = 240

    # To speed things up, lower the resolution of the camera
    CAMERA_WIDTH = 320
    CAMERA_HEIGHT = 240

    # Camera center of image
    cam_cx = CAMERA_WIDTH / 2
    cam_cy = CAMERA_HEIGHT / 2

    # Face detection opencv center of face box
    face_cx = cam_cx
    face_cy = cam_cy

    # Pan/Tilt motion center point
    pan_cx = pan_x_c
    pan_cy = pan_y_c

    # Amount pan/tilt moves when searching
    pan_move_x = 30
    pan_move_y = 20

    # Timer seconds to wait before starting pan/tilt search for face.
    # local face search
    face_timer1 = 10
    # Wide face search
    face_timer2 = 20

    # Park if search goes too long
    face_timer3 = 30
    pan_parked = False

    # load a cascade file for detecting faces. This file must be in
    # same folder as this script. Can usually be found as part of opencv
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Saving the picture to an in-program stream rather than a file
    stream = io.BytesIO()

    # Move the pan/tilt to a specific location. has built in limit checks.
    def pan_goto(x,y):
       p.do_pan (int(x))
       p.do_tilt (int(y))

    # Start Main Program
    with picamera.PiCamera() as camera:
       camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
       camera.vflip = True
       time.sleep(2)

       # Put camera in a known good position.
       pan_goto(pan_x_c, pan_y_c)
       face_found = False
       start_time = time.time()

       while(True):
          with picamera.array.PiRGBArray(camera) as stream:
             camera.capture(stream, format='bgr')
             # At this point the image is available as stream.array
             image = stream.array

          # Convert to grayscale, which is easier
          gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
          # Look for faces over the given image using the loaded cascade file
          faces = face_cascade.detectMultiScale(gray, 1.3, 5)

          for (x,y,w,h) in faces:
              if w > 0 :
                 face_found = True
                 pan_parked = False
                 start_time = time.time()

              # Opencv has built in image manipulation functions
              cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
              face_cx = x + w/2
              Nav_LR = cam_cx - face_cx
              pan_cx = pan_cx - Nav_LR /5

              face_cy = y + h/2
              Nav_UD = cam_cy - face_cy
              pan_cy = pan_cy - Nav_UD /4
              pan_goto(pan_cx, pan_cy)

              # Print Navigation required to center face in image
              print " Nav LR=%s UD=%s " % (Nav_LR, Nav_UD)

          elapsed_time = time.time() - start_time

          # start pan/tilt search for face if timer runs out
          if elapsed_time > face_timer3:
              if not pan_parked:
                 pan_goto(pan_x_c, pan_y_c)
                 print "Waiting for Face ....."
                 pan_parked = True

          elif elapsed_time > face_timer2:
              face_found = False
              print "Doing Wide Search   Timer2=%d  > %s seconds" % (elapsed_time, face_timer2)
              pan_cx = pan_cx + pan_move_x
              if pan_cx > limit_x_right:
                 pan_cx = limit_x_left
                 pan_cy = pan_cy + pan_move_y
                 if pan_cy > limit_y_top:
                    pan_cy = limit_y_bottom
              pan_goto (pan_cx, pan_cy)

          elif elapsed_time > face_timer1:
              face_found = False
              print "Doing Local Search  Timer1=%d  > %s seconds" % (elapsed_time, face_timer1)
              pan_cx = pan_cx + pan_move_x
              if (pan_cx > limit_x_right - (pan_move_x * 2)):
                 pan_cx = limit_x_left + pan_move_x
                 pan_cy = pan_cy + pan_move_y
                 if (pan_cy > limit_y_top - pan_move_y):
                    pan_cy = limit_y_bottom + pan_move_y
              pan_goto (pan_cx, pan_cy)

          # Use opencv built in window to show the image
          # Leave out if your Raspberry Pi isn't set up to display windows
          cv2.imshow('Test Image', image)

          if cv2.waitKey(1) & 0xFF == ord('q'):
             # Close Window
             cv2.destroyAllWindows()
             break
