/*
  Originally acquired from the following location by user Miles:
  http://www.maclife.com/forums/post/1623526#p1623526

  I have no idea what licensing terms this would be distributed under,
  though I figure they're fairly liberal since the code was posted
  on a public forum.

  to compile:
  gcc -o movemouse movemouse.m -framework ApplicationServices -framework Foundation
*/

#include <ApplicationServices/ApplicationServices.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
    if (argc == 3) {
        char *arg1end, *arg2end;
        float x = strtof(argv[1], &arg1end);
        float y = strtof(argv[2], &arg2end);
        if (!((x == 0.0 && argv[1] == arg1end) || (y == 0.0 && argv[2] == arg2end))) {
            CGEventRef ev = CGEventCreateMouseEvent(NULL, kCGEventMouseMoved, CGPointMake(x, y), kCGMouseButtonLeft);
            CGEventPost(kCGHIDEventTap, ev);
            CFRelease(ev);
            return 0;
        }
    }
    printf("usage: %s x y\n", argv[0]);
    return 1;
}
