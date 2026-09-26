# armyoftworecomp - ReXGlue Recompiled Project
#
# SDK boilerplate lives in generated/rexglue.cmake.

cmake_minimum_required(VERSION 3.25)
project(armyoftworecomp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

 set(REXSDK_VERSION "0.10.0.8-dev.g1406e1b")

# Fetch the ReXGlue SDK for this platform into rexglue/<platform> if not
# already present. Idempotent: existing SDK folders are left untouched.
# Version and platform are passed explicitly so the script stays self-contained.
if(WIN32 AND CMAKE_SYSTEM_PROCESSOR MATCHES "^(AMD64|x86_64)$")
    set(REXSDK_PLATFORM "win-amd64")
elseif(WIN32 AND CMAKE_SYSTEM_PROCESSOR MATCHES "^ARM64$")
    message(FATAL_ERROR "win-arm64 ReXGlue SDK release is not published")
elseif(APPLE AND CMAKE_OSX_ARCHITECTURES MATCHES "arm64")
    set(REXSDK_PLATFORM "mac-arm64")
elseif(APPLE)
    set(REXSDK_PLATFORM "mac-amd64")
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^(aarch64|arm64)$")
    set(REXSDK_PLATFORM "linux-arm64")
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^(x86_64|AMD64)$")
    set(REXSDK_PLATFORM "linux-amd64")
else()
    message(FATAL_ERROR "Unsupported platform: ${CMAKE_SYSTEM_PROCESSOR}")
endif()

execute_process(
    COMMAND ${CMAKE_COMMAND}
            "-DREXSDK_VERSION='${REXSDK_VERSION}'"
            "-DREXSDK_PLATFORM=${REXSDK_PLATFORM}"
            -P "${CMAKE_CURRENT_SOURCE_DIR}/cmake/fetch-rexglue-sdk.cmake")

 set(REXSDK_VERSION "")

# Find the fetched SDK with any preset, not only the local-* ones from
# CMakeUserPresets.json (Visual Studio configures the first preset on open).
list(PREPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_SOURCE_DIR}/rexglue/${REXSDK_PLATFORM}")

# First configure on a fresh clone: generated/default/sources.cmake only exists
# after `rexglue codegen`, and without it the recomp target is not created.
# assets/default.xex must be in place before this runs (see README).
set(ARMYOFTWORECOMP_GENERATED_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/generated/default/sources.cmake")
if(NOT EXISTS "${ARMYOFTWORECOMP_GENERATED_SOURCES}")
    set(ARMYOFTWORECOMP_REXGLUE_EXE
        "${CMAKE_CURRENT_SOURCE_DIR}/rexglue/${REXSDK_PLATFORM}/bin/rexglue${CMAKE_EXECUTABLE_SUFFIX}")
    if(EXISTS "${ARMYOFTWORECOMP_REXGLUE_EXE}")
        message(STATUS "[armyoftworecomp] generated/default/sources.cmake missing - running codegen once")
        execute_process(
            COMMAND "${ARMYOFTWORECOMP_REXGLUE_EXE}" codegen "${CMAKE_CURRENT_SOURCE_DIR}/armyoftworecomp_manifest.toml"
            WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
            RESULT_VARIABLE ARMYOFTWORECOMP_CODEGEN_RESULT)
        if(NOT ARMYOFTWORECOMP_CODEGEN_RESULT EQUAL 0)
            message(WARNING "[armyoftworecomp] bootstrap codegen failed (${ARMYOFTWORECOMP_CODEGEN_RESULT}); "
                            "the build-time codegen step will report the errors")
        endif()
    endif()
endif()
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${ARMYOFTWORECOMP_GENERATED_SOURCES}")

include(generated/rexglue.cmake)

# temporary disabled
#include(cmake/build_optimizations.cmake)

set(ARMYOFTWORECOMP_SOURCES
    src/main.cpp
)

if(WIN32)
    list(APPEND ARMYOFTWORECOMP_SOURCES
        src/armyoftworecomp.rc
    )
endif()

if(WIN32)
    add_executable(armyoftworecomp WIN32 ${ARMYOFTWORECOMP_SOURCES})
else()
    add_executable(armyoftworecomp ${ARMYOFTWORECOMP_SOURCES})
endif()

rexglue_setup_target(armyoftworecomp GPU_PLUGINS xenos)

# SDL looks for this file (name set by settings/mapping.toml's
# hid_mappings_file) next to the exe at startup to fill in gamepads it
# doesn't already recognize. Sourced from
# https://github.com/mdqinc/SDL_GameControllerDB, see settings/README.md.
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/settings/gamecontrollerdb.txt")
    add_custom_command(TARGET armyoftworecomp POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${CMAKE_CURRENT_SOURCE_DIR}/settings/gamecontrollerdb.txt"
                "$<TARGET_FILE_DIR:armyoftworecomp>/gamecontrollerdb.txt"
        COMMENT "Copying gamecontrollerdb.txt next to armyoftworecomp.exe")
endif()
