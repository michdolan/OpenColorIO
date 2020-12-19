# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the OpenColorIO Project.
#
# Locate or install openexr
#
# Variables defined by this module:
#   OpenEXR_FOUND - If FALSE, do not try to link to openexr
#   OpenEXR_LIBRARY - OpenEXR library to link to
#   OpenEXR_INCLUDE_DIR - Where to find OpenEXR and IlmBase headers
#   OpenEXR_VERSION - The version of the library
#
# Imported targets defined by this module, if found:
#   OpenEXR::IlmImf
#   OpenEXR::IlmImfUtil
#   IlmBase::Half
#   IlmBase::Iex
#   IlmBase::IexMath
#   IlmBase::IlmThread
#   IlmBase::Imath
#
# By default, the dynamic libraries of openexr will be found. To find the 
# static ones instead, you must set the OpenEXR_STATIC_LIBRARY variable to 
# TRUE before calling find_package(OpenEXR ...).
#
# If OpenEXR is not installed in a standard path, you can use the 
# OpenEXR_ROOT variable to tell CMake where to find it. If it is not found 
# and OCIO_INSTALL_EXT_PACKAGES is set to MISSING or ALL, OpenEXR will be 
# downloaded, built, and statically-linked into libOpenColorIO at build time.
#

# OpenEXR components may have the version in their name
set(_OpenEXR_LIB_VER "${OpenEXR_FIND_VERSION_MAJOR}_${OpenEXR_FIND_VERSION_MINOR}")

###############################################################################
### Try to find package ###

if(NOT OCIO_INSTALL_EXT_PACKAGES STREQUAL ALL)
    set(_OpenEXR_REQUIRED_VARS OpenEXR_LIBRARY)

    if(NOT DEFINED OpenEXR_ROOT)
        # Search for IlmBaseConfig.cmake
        find_package(IlmBase ${OpenEXR_FIND_VERSION} CONFIG QUIET)
    endif()

    if(OpenEXR_FOUND)
        get_target_property(OpenEXR_LIBRARY IlmBase::OpenEXR LOCATION)
    else()
        list(APPEND _OpenEXR_REQUIRED_VARS OpenEXR_INCLUDE_DIR)

        # Search for IlmBase.pc
        find_package(PkgConfig QUIET)
        pkg_check_modules(PC_IlmBase QUIET "IlmBase>=${OpenEXR_FIND_VERSION}")

        # Find include directory
        find_path(OpenEXR_INCLUDE_DIR
            NAMES
                OpenEXR/OpenEXR.h
            HINTS
                ${OpenEXR_ROOT}
                ${PC_OpenEXR_INCLUDE_DIRS}
            PATH_SUFFIXES
                include
                OpenEXR/include
        )

        # Lib names to search for
        set(_OpenEXR_LIB_NAMES "OpenEXR-${_OpenEXR_LIB_VER}" OpenEXR)
        if(BUILD_TYPE_DEBUG)
            # Prefer Debug lib names
            list(INSERT _OpenEXR_LIB_NAMES 0 "OpenEXR-${_OpenEXR_LIB_VER}_d")
        endif()

        if(OpenEXR_STATIC_LIBRARY)
            # Prefer static lib names
            set(_OpenEXR_STATIC_LIB_NAMES 
                "${CMAKE_STATIC_LIBRARY_PREFIX}OpenEXR-${_OpenEXR_LIB_VER}${CMAKE_STATIC_LIBRARY_SUFFIX}"
                "${CMAKE_STATIC_LIBRARY_PREFIX}OpenEXR${CMAKE_STATIC_LIBRARY_SUFFIX}"
            )
            if(BUILD_TYPE_DEBUG)
                # Prefer static Debug lib names
                list(INSERT _OpenEXR_STATIC_LIB_NAMES 0
                    "${CMAKE_STATIC_LIBRARY_PREFIX}OpenEXR-${_OpenEXR_LIB_VER}_d${CMAKE_STATIC_LIBRARY_SUFFIX}")
            endif()
        endif()

        # Find library
        find_library(OpenEXR_LIBRARY
            NAMES
                ${_OpenEXR_STATIC_LIB_NAMES} 
                ${_OpenEXR_LIB_NAMES}
            HINTS
                ${OpenEXR_ROOT}
                ${PC_OpenEXR_LIBRARY_DIRS}
            PATH_SUFFIXES
                lib64 lib 
        )

        # Get version from config header file
        if(OpenEXR_INCLUDE_DIR)
            if(EXISTS "${OpenEXR_INCLUDE_DIR}/OpenEXR/IlmBaseConfig.h")
                set(_OpenEXR_CONFIG "${OpenEXR_INCLUDE_DIR}/OpenEXR/IlmBaseConfig.h")
            elseif(EXISTS "${OpenEXR_INCLUDE_DIR}/OpenEXR/OpenEXRConfig.h")
                set(_OpenEXR_CONFIG "${OpenEXR_INCLUDE_DIR}/OpenEXR/OpenEXRConfig.h")
            endif()
        endif()

        if(_OpenEXR_CONFIG)
            file(STRINGS "${_OpenEXR_CONFIG}" _OpenEXR_VER_SEARCH 
                REGEX "^[ \t]*#define[ \t]+(OPENEXR|ILMBASE)_VERSION_STRING[ \t]+\"[.0-9]+\".*$")
            if(_OpenEXR_VER_SEARCH)
                string(REGEX REPLACE ".*#define[ \t]+(OPENEXR|ILMBASE)_VERSION_STRING[ \t]+\"([.0-9]+)\".*" 
                    "\\2" OpenEXR_VERSION "${_OpenEXR_VER_SEARCH}")
            endif()
        elseif(PC_OpenEXR_FOUND)
            set(OpenEXR_VERSION "${PC_OpenEXR_VERSION}")
        endif()
    endif()

    # Override REQUIRED if package can be installed
    if(OCIO_INSTALL_EXT_PACKAGES STREQUAL MISSING)
        set(OpenEXR_FIND_REQUIRED FALSE)
    endif()

    include(FindPackageHandleStandardArgs)
    find_package_handle_standard_args(OpenEXR
        REQUIRED_VARS 
            ${_OpenEXR_REQUIRED_VARS}
        VERSION_VAR
            OpenEXR_VERSION
    )
endif()

###############################################################################
### Create target

if (NOT TARGET IlmBase::OpenEXR)
    add_library(IlmBase::OpenEXR UNKNOWN IMPORTED GLOBAL)
    set(_OpenEXR_TARGET_CREATE TRUE)
endif()

###############################################################################
### Install package from source ###

if(NOT OpenEXR_FOUND)
    include(ExternalProject)
    include(GNUInstallDirs)

    if(APPLE)
        set(CMAKE_OSX_DEPLOYMENT_TARGET ${CMAKE_OSX_DEPLOYMENT_TARGET})
    endif()

    set(_EXT_DIST_ROOT "${CMAKE_BINARY_DIR}/ext/dist")
    set(_EXT_BUILD_ROOT "${CMAKE_BINARY_DIR}/ext/build")

    # Set find_package standard args
    set(OpenEXR_FOUND TRUE)
    set(OpenEXR_VERSION ${OpenEXR_FIND_VERSION})
    set(OpenEXR_INCLUDE_DIR "${_EXT_DIST_ROOT}/${CMAKE_INSTALL_INCLUDEDIR}")

    # Set the expected library name. "_d" is appended to Debug Windows builds 
    # <= OpenEXR 2.3.0. In newer versions, it is appended to Debug libs on
    # all platforms.
    if(BUILD_TYPE_DEBUG AND (WIN32 OR OpenEXR_VERSION VERSION_GREATER "2.3.0"))
        set(_OpenEXR_LIB_SUFFIX "_d")
    endif()

    set(OpenEXR_LIBRARY
        "${_EXT_DIST_ROOT}/${CMAKE_INSTALL_LIBDIR}/${CMAKE_STATIC_LIBRARY_PREFIX}OpenEXR-${_OpenEXR_LIB_VER}${_OpenEXR_LIB_SUFFIX}${CMAKE_STATIC_LIBRARY_SUFFIX}")

    if(_OpenEXR_TARGET_CREATE)
        if(UNIX)
            set(OpenEXR_CXX_FLAGS "${OpenEXR_CXX_FLAGS} -fPIC")
        endif()

        if(MSVC)
            set(OpenEXR_CXX_FLAGS "${OpenEXR_CXX_FLAGS} /EHsc")
        endif()

        string(STRIP "${OpenEXR_CXX_FLAGS}" OpenEXR_CXX_FLAGS)
 
        set(OpenEXR_CMAKE_ARGS
            ${OpenEXR_CMAKE_ARGS}
            -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
            -DCMAKE_CXX_FLAGS=${OpenEXR_CXX_FLAGS}
            -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
            -DCMAKE_INSTALL_MESSAGE=${CMAKE_INSTALL_MESSAGE}
            -DCMAKE_INSTALL_PREFIX=${_EXT_DIST_ROOT}
            -DCMAKE_OBJECT_PATH_MAX=${CMAKE_OBJECT_PATH_MAX}
            -DBUILD_SHARED_LIBS=OFF
            -DBUILD_TESTING=OFF
            -DOPENEXR_VIEWERS_ENABLE=OFF
            -DPYILMBASE_ENABLE=OFF
        )

        if(CMAKE_TOOLCHAIN_FILE)
            set(OpenEXR_CMAKE_ARGS
                ${OpenEXR_CMAKE_ARGS} -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE})
        endif()

        # Hack to let imported target be built from ExternalProject_Add
        file(MAKE_DIRECTORY ${OpenEXR_INCLUDE_DIR})

        ExternalProject_Add(ilmbase_install
            GIT_REPOSITORY "https://github.com/openexr/openexr.git"
            GIT_TAG "v${OpenEXR_VERSION}"
            GIT_CONFIG advice.detachedHead=false
            GIT_SHALLOW TRUE
            PREFIX "${_EXT_BUILD_ROOT}/openexr"
            BUILD_BYPRODUCTS ${OpenEXR_LIBRARY}
            CMAKE_ARGS ${OpenEXR_CMAKE_ARGS}
            PATCH_COMMAND
                ${CMAKE_COMMAND} -P "${CMAKE_SOURCE_DIR}/share/cmake/scripts/PatchOpenEXR.cmake"
            BUILD_COMMAND
                ${CMAKE_COMMAND} --build .
                                 --config ${CMAKE_BUILD_TYPE}
                                 --target OpenEXR
            INSTALL_COMMAND
                ${CMAKE_COMMAND} -DCMAKE_INSTALL_CONFIG_NAME=${CMAKE_BUILD_TYPE}
                                 -P "IlmBase/OpenEXR/cmake_install.cmake"
            EXCLUDE_FROM_ALL TRUE
        )

        add_dependencies(IlmBase::OpenEXR ilmbase_install)
        message(STATUS "Installing OpenEXR (IlmBase): ${OpenEXR_LIBRARY} (version \"${OpenEXR_VERSION}\")")
    endif()
endif()

###############################################################################
### Configure target ###

if(_OpenEXR_TARGET_CREATE)
    set_target_properties(IlmBase::OpenEXR PROPERTIES
        IMPORTED_LOCATION ${OpenEXR_LIBRARY}
        INTERFACE_INCLUDE_DIRECTORIES ${OpenEXR_INCLUDE_DIR}
    )

    mark_as_advanced(OpenEXR_INCLUDE_DIR OpenEXR_LIBRARY OpenEXR_VERSION)
endif()
