# *****************************************************************************
#
# DESCRIPTION: Script for build tool cmake on both unix and windows
#
# *****************************************************************************
#
# Copyright 2003-2024 by Wilson Snyder. This program is free software; you can
# redistribute it and/or modify it under the terms of either the GNU Lesser
# General Public License Version 3 or the Perl Artistic License Version 2.0.
# SPDX-License-Identifier: LGPL-3.0-only OR Artistic-2.0
#
# ****************************************************************************/

cmake_minimum_required(VERSION 3.24)
cmake_policy(SET CMP0091 NEW) # Use MSVC_RUNTIME_LIBRARY to select the runtime
project(Verilator
    VERSION 5.025
    HOMEPAGE_URL https://verilator.org
    LANGUAGES CXX
)

find_package(Python3 COMPONENTS Interpreter REQUIRED)
find_package(PkgConfig REQUIRED)
set(PYTHON3 Python3::Interpreter)
set(CMAKE_INSTALL_DATADIR ${CMAKE_INSTALL_PREFIX})
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
include(CheckStructHasMember)
include(ExternalProject)
include(CheckIPOSupported)

option(
  DEBUG_AND_RELEASE_AND_COVERAGE
  "Builds both the debug and release binaries, overriding CMAKE_BUILD_TYPE. \
  Not supported under MSBuild.")

option(ENABLE_CCWARN "Enable extra warnings, and convert them to errors." ON)

option(ENABLE_LTO "Enable Link Time Optimization" OFF)

option(GENERATE_COMPILE_COMMANDS "Generate compile_commands.json" ON)

pkg_check_modules(TCMALLOC libtcmalloc_minimal)
option(TCMALLOC_ENABLED "Compile Verilator with tcmalloc" OFF)

pkg_check_modules(JEMALLOC jemalloc)
option(JEMALLOC_ENABLED "Compile Verilator with jemalloc" OFF)

# pkg_check_modules(MIMALLOC mimalloc)
# set(MIMALLOC
#     ""
#     CACHE STRING "Compile Verilator with mimalloc" OFF)

if(NOT WIN32)
  message(WARNING "CMake support on Linux/OSX is experimental.")
endif()

if(WIN32)
  if(DEFINED ENV{WIN_FLEX_BISON})
    set(WIN_FLEX_BISON "$ENV{WIN_FLEX_BISON}")
  endif()
  if(EXISTS ${WIN_FLEX_BISON})
    list(APPEND CMAKE_PREFIX_PATH ${WIN_FLEX_BISON})
  endif()
  if(NOT WIN_FLEX_BISON)
    message(
      FATAL_ERROR
        "Please install https://github.com/lexxmark/winflexbison and set \
        WIN_FLEX_BISON environment variable. Please use install cmake \
        target after a successful build.")
  endif()
  set(CMAKE_CXX_STANDARD 20)
endif()

if(NOT CMAKE_BUILD_TYPE)
  error("%Error: CMAKE_BUILD_TYPE must be set")
endif()

if(CMAKE_CURRENT_SOURCE_DIR STREQUAL CMAKE_CURRENT_BINARY_DIR AND NOT MSVC_IDE)
  error("%Error: In-source builds are not allowed.")
endif()

set(OBJCACHE
    ""
    CACHE STRING "Path for ccache, auto-detected if empty")
option(OBJCACHE_ENABLED "Compile Verilator with ccache" ON)

if(OBJCACHE_ENABLED)
  if(OBJCACHE STREQUAL "")
    find_program(OBJCACHE_PATH ccache)
    if(OBJCACHE_PATH STREQUAL "OBJCACHE_PATH-NOTFOUND")
      set(OBJCACHE_PATH "")
    endif()
  else()
    set(OBJCACHE_PATH "${OBJCACHE}")
  endif()
  if(NOT OBJCACHE_PATH STREQUAL "")
    execute_process(COMMAND "${OBJCACHE_PATH}" --version
                    OUTPUT_VARIABLE objcache_version)
    string(REGEX MATCH "[^\n\r]+" objcache_version "${objcache_version}")
    message(STATUS "Found ccache: ${OBJCACHE_PATH} (\"${objcache_version}\")")
    set(CMAKE_CXX_COMPILER_LAUNCHER "${OBJCACHE_PATH}")
  endif()
endif()

set(MOLD
    ""
    CACHE STRING "Path for mold, auto-detected if empty")
option(MOLD_ENABLED "Compile Verilator with ccache" ON)

if(MOLD_ENABLED)
  if(MOLD STREQUAL "")
    find_program(MOLD_PATH mold)
    if(MOLD_PATH STREQUAL "MOLD_PATH-NOTFOUND")
      set(MOLD_PATH "")
    endif()
  else()
    set(MOLD_PATH "${MOLD}")
  endif()
  if(NOT MOLD_PATH STREQUAL "")
    execute_process(COMMAND "${MOLD_PATH}" --version
                    OUTPUT_VARIABLE mold_version)
    string(REGEX MATCH "[^\n\r]+" mold_version "${mold_version}")
    message(STATUS "Found mold: ${MOLD_PATH} (\"${mold_version}\")")
    set(CMAKE_LINKER "${MOLD_PATH}")
    set(CMAKE_EXE_LINKER_FLAGS "-fuse-ld=mold")
    set(CMAKE_SHARED_LINKER_FLAGS "-fuse-ld=mold")
  endif()
endif()

option(FULL_STATIC "Link Verilator completely statically")
if(FULL_STATIC)
  set(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
  set(BUILD_SHARED_LIBS OFF)
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} \
    -static-libgcc -static-libstdc++ -static -Xlinker -gc-sections")
endif()

find_package(BISON REQUIRED)
find_package(FLEX REQUIRED)

# Build set_property(GLOBAL PROPERTY JOB_POOLS one_job=1)

if(GENERATE_COMPILE_COMMANDS)
  set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
endif()

if(DEBUG_AND_RELEASE_AND_COVERAGE)
  if(CMAKE_GENERATOR MATCHES "^Visual Studio ")
    error("%Error: The DEBUG_AND_RELEASE_AND_COVERAGE option is not \
      supported in MSBuild-based builds.")
  endif()
  set(SAVED_BUILD_TYPE ${CMAKE_BUILD_TYPE})
  set(CMAKE_BUILD_TYPE Debug)
  add_subdirectory(src build-Debug)
  set(CMAKE_BUILD_TYPE Release)
  add_subdirectory(src build-Release)
  set(CMAKE_BUILD_TYPE Coverage)
  add_subdirectory(src build-Coverage)
  set(CMAKE_BUILD_TYPE ${SAVED_BUILD_TYPE})
else()
  add_subdirectory(src)
endif()

# Configuration and Installation

set(PACKAGE_NAME ${PROJECT_NAME})
set(PACKAGE_VERSION ${PROJECT_VERSION})

configure_file(include/verilated_config.h.in include/verilated_config.h @ONLY)

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/include/verilated_config.h
        DESTINATION ${CMAKE_INSTALL_PREFIX}/include)

configure_package_config_file(verilator-config.cmake.in verilator-config.cmake
                              INSTALL_DESTINATION ${CMAKE_INSTALL_PREFIX})

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/verilator-config.cmake
        DESTINATION ${CMAKE_INSTALL_PREFIX})

configure_package_config_file(
  verilator-config-version.cmake.in verilator-config-version.cmake
  INSTALL_DESTINATION ${CMAKE_INSTALL_PREFIX})

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/verilator-config-version.cmake
        DESTINATION ${CMAKE_INSTALL_PREFIX})

foreach(program verilator verilator_gantt verilator_ccache_report
                verilator_difftree verilator_profcfunc)
  install(PROGRAMS bin/${program} TYPE BIN)
endforeach()

install(
  DIRECTORY examples
  TYPE DATA
  FILES_MATCHING
  PATTERN "examples/*/*.[chv]*"
  PATTERN "examples/*/Makefile*"
  PATTERN "examples/*/CMakeLists.txt")

install(
  DIRECTORY include
  TYPE DATA
  FILES_MATCHING
  PATTERN "include/verilated_config.h"
  PATTERN "include/verilated.mk"
  PATTERN "include/*.[chv]"
  PATTERN "include/*.cpp"
  PATTERN "include/*.sv"
  PATTERN "include/gtkwave/*.[chv]*"
  PATTERN "include/vltstd/*.[chv]*")

# enable_testing()

# add_test( NAME verilator COMMAND make -C test_regress WORKING_DIRECTORY
# ${CMAKE_CURRENT_SOURCE_DIR} )

# set_property(TEST verilator PROPERTY ENVIRONMENT
# "VERILATOR_ROOT=${CMAKE_BINARY_DIR}")

# set(VERILATOR_ROOT ${CMAKE_BINARY_DIR})


add_custom_target(
  check
  COMMAND perl driver.pl -j 0 --quiet --rerun --vlt --vltmt --dist
  DEPENDS ${VERILATOR}
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/test_regress
  USES_TERMINAL
  COMMENT "Running regression tests")
