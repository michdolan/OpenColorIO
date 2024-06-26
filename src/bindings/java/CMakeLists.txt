# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the OpenColorIO Project.

find_package(Java REQUIRED)
find_package(JNI REQUIRED)

set(SOURCES
	JNIBaker.cpp
	JNIColorSpace.cpp
	JNIConfig.cpp
	JNIContext.cpp
	JNIGlobals.cpp
	JNIGpuShaderDesc.cpp
	JNIImageDesc.cpp
	JNILook.cpp
	JNIProcessor.cpp
	JNITransforms.cpp
	JNIUtil.cpp
)

set(JNIOCIO_JAVAS
	org/OpenColorIO/Allocation.java
	org/OpenColorIO/AllocationTransform.java
	org/OpenColorIO/Baker.java
	org/OpenColorIO/BitDepth.java
	org/OpenColorIO/CDLTransform.java
	org/OpenColorIO/ColorSpaceDirection.java
	org/OpenColorIO/ColorSpace.java
	org/OpenColorIO/ColorSpaceTransform.java
	org/OpenColorIO/Config.java
	org/OpenColorIO/Context.java
	org/OpenColorIO/DisplayTransform.java
	org/OpenColorIO/EnvironmentMode.java
	org/OpenColorIO/ExceptionBase.java
	org/OpenColorIO/ExceptionMissingFile.java
	org/OpenColorIO/ExponentTransform.java
	org/OpenColorIO/FileTransform.java
	org/OpenColorIO/Globals.java
	org/OpenColorIO/GpuLanguage.java
	org/OpenColorIO/GpuShaderDesc.java
	org/OpenColorIO/GroupTransform.java
	org/OpenColorIO/ImageDesc.java
	org/OpenColorIO/Interpolation.java
	org/OpenColorIO/LoggingLevel.java
	org/OpenColorIO/LogTransform.java
	org/OpenColorIO/Look.java
	org/OpenColorIO/LookTransform.java
	org/OpenColorIO/MatrixTransform.java
	org/OpenColorIO/PackedImageDesc.java
	org/OpenColorIO/PlanarImageDesc.java
	org/OpenColorIO/Processor.java
	org/OpenColorIO/TransformDirection.java
	org/OpenColorIO/Transform.java
)

set(JNIOCIO_CLASSES
  # Core
  org.OpenColorIO.ExceptionBase
  org.OpenColorIO.ExceptionMissingFile
  org.OpenColorIO.Globals
  org.OpenColorIO.Config
  org.OpenColorIO.ColorSpace
  org.OpenColorIO.Processor
  org.OpenColorIO.GpuShaderDesc
  org.OpenColorIO.Context
  org.OpenColorIO.Look
  org.OpenColorIO.ImageDesc
  org.OpenColorIO.Transform
  org.OpenColorIO.PackedImageDesc
  org.OpenColorIO.PlanarImageDesc
  org.OpenColorIO.Baker
  # Enums
  org.OpenColorIO.LoggingLevel
  org.OpenColorIO.ColorSpaceDirection
  org.OpenColorIO.TransformDirection
  org.OpenColorIO.Interpolation
  org.OpenColorIO.BitDepth
  org.OpenColorIO.Allocation
  org.OpenColorIO.GpuLanguage
  org.OpenColorIO.EnvironmentMode
  # Transforms
  org.OpenColorIO.AllocationTransform
  org.OpenColorIO.CDLTransform
  org.OpenColorIO.ColorSpaceTransform
  org.OpenColorIO.DisplayTransform
  org.OpenColorIO.ExponentTransform
  org.OpenColorIO.FileTransform
  org.OpenColorIO.GroupTransform
  org.OpenColorIO.LogTransform
  org.OpenColorIO.LookTransform
  org.OpenColorIO.MatrixTransform	
)

configure_file(Manifest.txt.in ${CMAKE_CURRENT_BINARY_DIR}/Manifest.txt @ONLY)
configure_file(LoadLibrary.java.in ${CMAKE_CURRENT_BINARY_DIR}/LoadLibrary.java @ONLY)
list(APPEND JNIOCIO_JAVAS ${CMAKE_CURRENT_BINARY_DIR}/LoadLibrary.java)

# Create OpenColorIOJNI.h that includes all the ocio jni headers
set(JNIOCIO_HEADERS "")
set(JNIOCIO_H_INCLUDE "/* DO NOT EDIT THIS FILE - it is machine generated */\n\n")
foreach(_CLASS ${JNIOCIO_CLASSES})
  string(REPLACE "." "_" _CLASS_H ${_CLASS})
  set(_CLASS_H "${_CLASS_H}.h")
  list(APPEND JNIOCIO_HEADERS "${_CLASS_H}")
  set(JNIOCIO_H_INCLUDE "${JNIOCIO_H_INCLUDE}#include \"${_CLASS_H}\"\n")
endforeach()

file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/OpenColorIOJNI.h" "${JNIOCIO_H_INCLUDE}")

###############################################################################
# Compile java classes

set(JNIOCIO_JAR "${CMAKE_CURRENT_BINARY_DIR}/OpenColorIO-${OpenColorIO_VERSION}.jar")
add_custom_target(JNI-directory
	COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/org/OpenColorIO
)

add_custom_command(OUTPUT ${JNIOCIO_HEADERS}
	COMMAND ${Java_JAVAC_EXECUTABLE} -cp ${CMAKE_CURRENT_BINARY_DIR} -d ${CMAKE_CURRENT_BINARY_DIR} ${JNIOCIO_JAVAS}
	DEPENDS ${JNIOCIO_JAVAS} JNI-directory
	WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
	COMMENT "Compiling .java files and creating jni C headers"
)
add_custom_command(OUTPUT ${JNIOCIO_JAR}
	COMMAND ${Java_JAVAH_EXECUTABLE} -jni -force ${JNIOCIO_CLASSES}
	COMMAND ${Java_JAR_EXECUTABLE} vcfm ${JNIOCIO_JAR} Manifest.txt org
	DEPENDS ${JNIOCIO_HEADERS} JNI-directory
	WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
	COMMENT "Creating .jar file"
)
###############################################################################
# Target Properties

add_library(OpenColorIO-JNI SHARED ${SOURCES} ${JNIOCIO_HEADERS} ${JNIOCIO_JAR})
target_include_directories(OpenColorIO-JNI
	PUBLIC
		org
		${CMAKE_CURRENT_BINARY_DIR}
		${JNI_INCLUDE_DIRS}
)

target_link_libraries(OpenColorIO-JNI
	PUBLIC
		OpenColorIO
)

set_target_properties(OpenColorIO-JNI
	PROPERTIES
		VERSION ${OpenColorIO_VERSION}
		SOVERSION ${SOVERSION}
)


###############################################################################
# Installation

install(TARGETS OpenColorIO-JNI
	DESTINATION ${CMAKE_INSTALL_EXEC_PREFIX}/${CMAKE_INSTALL_LIBDIR}
)
install(FILES ${JNIOCIO_JAR}
	DESTINATION ${CMAKE_INSTALL_PREFIX}/share/ocio/
)
