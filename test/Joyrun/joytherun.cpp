/*
    ---------------------------------------------

    filename: joytherun.cpp

    desc: magic numbers 7958378, 6645876, 7239026
                     to "joy",   "the",   "run"

    ---------------------------------------------

    利用 python 对其解释如下：

    In [206]: ord('j') + 256*ord('o') + 256*256*ord('y')
    Out[206]: 7958378

    In [207]: a = 7958378

    In [208]: chr(a % 256)
    Out[208]: 'j'

    In [209]: a //= 256

    In [210]: chr(a % 256)
    Out[210]: 'o'

    In [211]: a //= 256

    In [212]: chr(a % 256)
    Out[212]: 'y'

    In [213]: a //= 256

    In [214]: a
    Out[214]: 0

 */

#include <iostream>
#include <cstring>

using namespace std;

typedef int _DWORD;               // _DWORD 实际上是一个 4 bytes 32 bits 的整数类型
// typedef unsigned long _DWORD;  // 也可以定义成 unsigned long, g++ 编译成 8 bytes 64 bits

int main(void)
{
    char * str = new char[sizeof(_DWORD) / sizeof(char)];

    *(_DWORD *)str = 7958378;
    // *(_DWORD *)&str[0] = 7958378;

    cout << str << " " << strlen(str) << endl;

    *(_DWORD *)str = 6645876;
    // *(_DWORD *)&str[0] = 6645876;

    cout << str << " " << strlen(str) << endl;

    *(_DWORD *)str = 7239026;
    // *(_DWORD *)&str[0] = 7239026;

    cout << str << " " << strlen(str) << endl;

    delete [] str;

    return 0;
}
