TEMPLATE = app
CONFIG += console c++11
CONFIG -= app_bundle
CONFIG -= qt

### ensure this path points to opencv on your computer
INCLUDEPATH += C:\OpenCV31\build\include ### was c:/opencv31/release/install/include

### ensure thes paths points to mingw build on your computer
### note that opencv must be built to 32/64 bit to match mingw version
#LIBS += -LC:\opencv31\build\install\x86\mingw\lib
#LIBS += -LC:\opencv31\build\install\x86\mingw\bin
LIBS += -LC:\opencv31\build\lib
LIBS +=    -lopencv_core310 \
    -lopencv_highgui310 \
    -lopencv_imgproc310 \
    -lopencv_imgcodecs310 \
    -lopencv_features2d310 \
    -lopencv_calib3d310 \
    -lopencv_videoio310 \
    -lws2_32 \
##    -lopencv_ffmpeg310

SOURCES += 


HEADERS += 

