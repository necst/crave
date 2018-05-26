if(WIN32)
	set(CMAKE_BUILD_TYPE "Release")
    #SET_PROPERTY(DIRECTORY APPEND PROPERTY COMPILE_DEFINITIONS_RELEASE QT_NO_DEBUG)

	#set the default pathes, should be changed to match your setup.
	set(APP_RC ${CMAKE_CURRENT_SOURCE_DIR}/crossincludes/tester.rc)
	set(MINGW_INCLUDES ${CMAKE_CURRENT_SOURCE_DIR}/crossincludes/)

	set(MINGW_PREFIX "i686-w64-mingw32-")

	# set "sane" default cxxflags for windows, the -mwindows so it wouldn't open a command dos window.
	set(CMAKE_CXX_FLAGS_RELEASE  "${CMAKE_CXX_FLAGS_RELEASE} -m32 -mwindows")
	# we need -static-libgcc otherwise we'll link against libgcc_s_sjlj-1.dll.
    if(STATICDROPPER)
        SET(CMAKE_SHARED_LIBRARY_LINK_CXX_FLAGS "-Wl,--no-undefined -static-libgcc -Wl,-Bstatic -lstdc++ -lpthread -Wl,-O1 -Wl,--as-needed -Wl,--sort-common -s")
    else()
	    SET(CMAKE_SHARED_LIBRARY_LINK_CXX_FLAGS "-Wl,--no-undefined -lstdc++ -lpthread -Wl,-O1 -Wl,--as-needed -Wl,--sort-common -s")
    endif()

	#you should NOT mess with things below this line.

	#set mingw defaults
	set(CMAKE_CXX_COMPILER ${MINGW_PREFIX}g++)
	set(CMAKE_AR           ${MINGW_PREFIX}ar)
	set(CMAKE_RANLIB       ${MINGW_PREFIX}ranlib)
	set(CMAKE_LINKER       ${MINGW_PREFIX}ld)
	set(CMAKE_STRIP        ${MINGW_PREFIX}strip)

	set(CMAKE_EXECUTABLE_SUFFIX ".exe") # if we don't do this, it'll output executables without the .exe suffix

	# add an icon to the exe if we set one.
	if(APP_RC)
		set(WIN32_ICON_O ${CMAKE_CURRENT_BINARY_DIR}/_app_rc.o)
		ADD_CUSTOM_COMMAND( OUTPUT ${WIN32_ICON_O}
							COMMAND ${MINGW_PREFIX}windres
								-I${MINGW_INCLUDES}
                                #								-I${CMAKE_CURRENT_SOURCE_DIR}
								-o${WIN32_ICON_O}
								-i${APP_RC}
							)
	endif()

	message("Building For   : Win32")
# else()
#	include(${linux resources})
endif()
