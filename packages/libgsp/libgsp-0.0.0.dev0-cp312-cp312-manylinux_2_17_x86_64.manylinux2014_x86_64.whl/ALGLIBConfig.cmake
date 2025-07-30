

set(ALGLIB_VERSION 4.0.4) 

# Include directories
set(ALGLIB_INCLUDE_DIRS ${CMAKE_CURRENT_LIST_DIR}/includes)
# Library directories
set(ALGLIB_LIBRARY_DIRS ${CMAKE_CURRENT_LIST_DIR}/libs)

set(ALGLIB_LIBRARIES ${ALGLIB_LIBRARY_DIRS}/libalglib.a)

if(NOT ALGLIB_LIBRARIES)
    message(FATAL_ERROR "ALGLIB library not found in ${ALGLIB_LIBRARY_DIRS}")
endif()


message(STATUS "ALGLIB libraries: ${ALGLIB_LIBRARIES}")

# Add imported target
add_library(alglib UNKNOWN IMPORTED)

set_target_properties(alglib PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES ${ALGLIB_INCLUDE_DIRS}
    IMPORTED_LOCATION ${ALGLIB_LIBRARIES}
)

set(ALGLIB_BUILD_SHARED_LIBS OFF)

# Define the operating system macro
target_compile_definitions(alglib INTERFACE AE_OS=AE_POSIX)
