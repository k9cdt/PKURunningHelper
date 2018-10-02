// test.cpp

#include <iostream>
#include <cstring>
#include <string>
#include "md5.h"

using namespace std;

typedef int _DWORD;

int main(void)
{
    char str1[] = "po";
    char str2[] = "1538284879";
    char str3[] = "153828487712981546";

    char * str0 = new char[strlen(str1) + strlen(str2) + strlen(str3) + 20];

    memcpy(str0, "raowenyuan", 11);
    cout << str0 << endl;

    strcat(str0, str1);
    cout << str0 << endl;

    *(_DWORD *)&str0[strlen(str0)] = 7958378;
    cout << str0 << endl;

    strcat(str0, str2);
    cout << str0 << endl;

    *(_DWORD *)&str0[strlen(str0)] = 6645876;
    cout << str0 << endl;

    strcat(str0, str3);
    cout << str0 << endl;

    *(_DWORD *)&str0[strlen(str0)] = 7239026;
    cout << str0 << endl;

    string sn0 = MD5(str0).hexdigest();
    string sn1 = "e4b8e9359e86247954f831cea60abc75";

    cout << sn0 << endl << sn1 << endl << (bool)(sn0 == sn1) << endl;

    delete [] str0;
    return 0;
}
