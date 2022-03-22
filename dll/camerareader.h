#ifndef CAMERAREADER_H
#define CAMERAREADER_H

#include "cameraReader_global.h"

extern "C" {
    __declspec(dllexport) void nokovInit(int ip);
    __declspec(dllexport) void nokovClose();
    __declspec(dllexport) void getImage(unsigned char *data);
}


#endif // CAMERAREADER_H
