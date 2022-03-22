#ifndef CAMERAREADER_H
#define CAMERAREADER_H

#include "cameraReader_global.h"

extern "C" {
    extern void nokovInit(int ip);
    extern void nokovClose();
    extern void getImage(unsigned char *data);
}


#endif // CAMERAREADER_H
