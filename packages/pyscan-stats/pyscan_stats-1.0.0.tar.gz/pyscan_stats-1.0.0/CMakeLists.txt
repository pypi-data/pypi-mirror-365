cmake_minimum_required(VERSION 3.5)
project(pyscan LANGUAGES CXX)

set(Python_EXECUTABLE "${PYTHON_EXECUTABLE}")
set(Python_INCLUDE_DIR "${PYTHON_INCLUDE_DIR}")
set(Python_LIBRARY "${PYTHON_LIBRARY}")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(PYBIND11_FINDPYTHON ON)
if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Need this for GSL
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_FLAGS_DEBUG "-fPIC -Wall -Wextra -g -O1 -fno-omit-frame-pointer")
set(CMAKE_CXX_FLAGS_RELEASE "-fPIC -w -O2 -march=native -DNDEBUG") #work for intel chip
set(CMAKE_C_FLAGS_DEBUG "-fPIC -Wall -Wextra -g -O1 -fno-omit-frame-pointer")
set(CMAKE_C_FLAGS_RELEASE "-fPIC -w -O2 -march=native -DNDEBUG") #work for intel chip

if(APPLE)
    # Add standard Homebrew prefix paths for macOS
    # To find CGAL, GSL, Boost installed via Homebrew
    list(APPEND CMAKE_PREFIX_PATH
        /opt/homebrew/opt
        /usr/local/opt
        /Users/${USER}/homebrew/opt
    )
    # Set Python3 to find static libraries and not frameworks
    # set(Python3_FIND_FRAMEWORK NEVER)
    # set(Python3_USE_STATIC_LIBS TRUE)
endif()


# Dependencies
find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)
find_package(Boost REQUIRED)
find_package(CGAL REQUIRED)
find_package(GSL REQUIRED)

# Build the thirdparty libraries
add_subdirectory(thirdparty/discrepancy)
add_subdirectory(thirdparty/kernel/ANN)
add_subdirectory(thirdparty/kernel/coreset)

# Core sources
file(GLOB_RECURSE CPP_SRC CONFIGURE_DEPENDS src/cpp/lib/*.cpp)

add_library(core_obj OBJECT ${CPP_SRC})

target_include_directories(core_obj PUBLIC
    ${CMAKE_SOURCE_DIR}/src/cpp/lib/include
    ${CMAKE_SOURCE_DIR}/thirdparty/discrepancy/include
    ${CMAKE_SOURCE_DIR}/thirdparty/kernel/ANN/include
    ${CMAKE_SOURCE_DIR}/thirdparty/kernel/coreset/include
    ${Boost_INCLUDE_DIRS}
)

target_link_libraries(core_obj PRIVATE pybind11::module ${Python3_LIBRARIES})

pybind11_add_module(libpyscan MODULE
    $<TARGET_OBJECTS:core_obj>
    src/cpp/bindings/libpyscan.cpp
)

set_target_properties(libpyscan PROPERTIES
    BUILD_RPATH "$ORIGIN"
    INSTALL_RPATH "$ORIGIN"
)

target_include_directories(ann PUBLIC
    ${CMAKE_SOURCE_DIR}/thirdparty/kernel/ANN/include
)
add_dependencies(libpyscan ann)

# Link libraries
target_link_libraries(libpyscan PRIVATE
    core_obj
    discrepancy
    ann
    appext
    CGAL::CGAL
    GSL::gsl
    GSL::gslcblas
)

set_target_properties(libpyscan PROPERTIES
    BUILD_RPATH "$ORIGIN"
    INSTALL_RPATH "$ORIGIN"
)

set_target_properties(ann PROPERTIES
    BUILD_RPATH "$ORIGIN"
    INSTALL_RPATH "$ORIGIN"
)

# Install Python module and dependencies into the `pyscan/` package dir
install(TARGETS libpyscan LIBRARY DESTINATION pyscan COMPONENT default)
install(FILES
    $<TARGET_FILE:discrepancy>
    $<TARGET_FILE:ann>
    $<TARGET_FILE:appext>
    DESTINATION pyscan
    COMPONENT default
)

option(PYSCAN_BUILD_TESTS "Build tests" OFF)
if(PYSCAN_BUILD_TESTS)

    message(STATUS "BUILDING TESTS")
    set(THIRDPARTY_LIBRARIES
        discrepancy
        ann
        appext
        CGAL::CGAL
        GSL::gsl
        GSL::gslcblas
    )
    
    include(CTest)
    enable_testing()
    include(FetchContent)
    FetchContent_Declare(
        googletest
        URL https://github.com/google/googletest/archive/release-1.12.1.zip
    )
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)
    set(TEST_NAMES
        DiskScan_unittest
        FunctionApprox_unittest
        Halfplane_unittest
        Testing_unittest
        Point_unittest
        RectangleScan_unittest
        trajectory_unittest
    )
    set(TEST_OUTPUT_DIR ${CMAKE_BINARY_DIR}/test)
    file(MAKE_DIRECTORY ${TEST_OUTPUT_DIR})

    foreach(TEST ${TEST_NAMES})
        add_executable(${TEST} test/${TEST}.cpp $<TARGET_OBJECTS:core_obj>)
        set_target_properties(${TEST} PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY ${TEST_OUTPUT_DIR}
        )
        target_link_libraries(${TEST} PRIVATE gtest_main ${THIRDPARTY_LIBRARIES})
        target_link_libraries(${TEST} PRIVATE ${Python3_LIBRARIES})
        target_include_directories(${TEST} PRIVATE ${CMAKE_SOURCE_DIR}/src/cpp/lib/include)
        target_include_directories(${TEST} PRIVATE ${Python3_INCLUDE_DIRS})
        include_directories(${pybind11_INCLUDE_DIRS})
        add_test(NAME ${TEST} COMMAND ${TEST})
        message(STATUS "Adding test: ${TEST} at binary dir ${TEST_OUTPUT_DIR}/${TEST}")
    endforeach()
endif()