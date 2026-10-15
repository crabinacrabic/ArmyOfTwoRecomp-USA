# armyoftworecomp - ReXGlue Recompiled Project
#
# SDK boilerplate lives in generated/rexglue.cmake.

cmake_minimum_required(VERSION 3.25)
project(armyoftworecomp LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Fix git symlinks on Windows (libmspack in SDK uses symlinks)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/fix_symlinks.cmake)

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/apply_sdk_patches.cmake)

include(cmake/build_optimizations.cmake)

# Build ReXGlue SDK from source (git submodule)
set(REXSDK_DIR "${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/rexglue-sdk" CACHE PATH "Path to rexglue-sdk source tree" FORCE)

# Enable both graphics backends
if(WIN32)
    set(REXGLUE_USE_D3D12 ON CACHE BOOL "Enable D3D12 graphics backend")
endif()
set(REXGLUE_USE_VULKAN ON CACHE BOOL "Enable Vulkan graphics backend")

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

set(ARMYOFTWORECOMP_SOURCES
    src/main.cpp
    src/game_patches.cpp
    src/game_cvars.cpp
    src/language_hook.cpp
    src/mouse/mouse_look.cpp
    src/mouse/ao2_camera_hook.cpp
    src/render/gpu_wait_hook.cpp
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
