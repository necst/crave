project(Dropper CXX)
cmake_minimum_required(VERSION 2.8.12)

include(lin-mingw.cmake)

set(SRCS     "source.cpp")

#it is safe to include ${WIN32_ICON_O}, if we're building for linux it'll be empty.
include_directories(${CMAKE_CURRENT_BINARY_DIR})
add_executable(tester ${SRCS} ${WIN32_ICON_O})
target_link_libraries(tester)
