// SPDX-License-Identifier: BSD-3-Clause
// Copyright Contributors to the OpenColorIO Project.

#ifndef INCLUDED_OCIO_IMAGEIO_H
#define INCLUDED_OCIO_IMAGEIO_H

#include <string>
#include <vector>

#include "OpenColorIO.h"

namespace OCIO_NAMESPACE
{

struct ChannelInfo
{
    std::string name;
    BitDepth bitDepth;
};

struct ImageInfo
{
    // Data window
    int x;
    int y;
    int width;
    int height;

    // Display window
    int fullX;
    int fullY;
    int fullWidth;
    int fullHeight;

    // Channels
    int channelCount;
    std::vector<ChannelInfo> channels;
};

ImageInfo GetImageInfo(const std::string & filename);

bool ReadImage(const std::string & filename, 
               const std::vector<std::string> & channelNames, 
               BitDepth bitDepth, 
               void * pixels);

bool WriteImage(const std::string & filename, 
                const ImageInfo & info,
                BitDepth bitDepth, 
                const void * pixels);

} // namespace OCIO_NAMESPACE

#endif // INCLUDED_OCIO_IMAGEIO_H
