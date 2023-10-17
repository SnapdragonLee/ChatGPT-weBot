cmake_minimum_required(VERSION 3.0.0)
project(wxinject VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D '_UNICODE' /D 'UNICODE' -O2")

set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)

enable_language(ASM_MASM)
set(CMAKE_ASM_NASM_FLAGS "-w0")

set(CMAKE_TOOLCHAIN_FILE "path/to/vcpkg.cmake")
set(CMAKE_PREFIX_PATH "path/to/vcpkg/lib_root")

file(GLOB CPP_FILES ${PROJECT_SOURCE_DIR}/src/*.cc ${PROJECT_SOURCE_DIR}/src/*.cpp ${PROJECT_SOURCE_DIR}/src/*.c)
file(GLOB ASM_FILES ${PROJECT_SOURCE_DIR}/src/*.asm)

find_package(nlohmann_json CONFIG REQUIRED)

find_path(DETOURS_INCLUDE_DIRS "detours/detours.h")
find_library(DETOURS_LIBRARY detours REQUIRED)

add_subdirectory(spdlog)
include_directories(${VCPKG_INSTALLED_DIR}/x64-windows/include ${PROJECT_SOURCE_DIR}/spdlog/include ${DETOURS_INCLUDE_DIRS})


add_library(wxinject SHARED ${CPP_FILES} ${ASM_FILES})

target_link_libraries(wxinject PRIVATE nlohmann_json::nlohmann_json)
target_link_libraries(wxinject PRIVATE spdlog::spdlog spdlog::spdlog_header_only)
target_link_libraries(wxinject PRIVATE ${DETOURS_LIBRARY})

SET_TARGET_PROPERTIES(wxinject PROPERTIES LINKER_LANGUAGE C
        ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/../bin
        LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/../bin
        RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/../bin
        OUTPUT_NAME "wxinject"
        PREFIX "")
           