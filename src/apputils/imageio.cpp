// SPDX-License-Identifier: BSD-3-Clause
// Copyright Contributors to the OpenColorIO Project.

#include <sstream>

#include "OpenEXR/half.h"
#include "OpenEXR/ImathBox.h"
#include "OpenEXR/ImfChannelList.h"
#include "OpenEXR/ImfFrameBuffer.h"
#include "OpenEXR/ImfHeader.h"
#include "OpenEXR/ImfInputFile.h"
#include "OpenEXR/ImfOutputFile.h"

#include "imageio.h"

namespace OCIO_NAMESPACE
{

namespace{

BitDepth pixelTypeToBitDepth(Imf::PixelType pixelType)
{
    BitDepth bitDepth;

    switch (pixelType)
    {
    case Imf::HALF:
        bitDepth = BIT_DEPTH_F16;
        break;
    case Imf::FLOAT:
        bitDepth = BIT_DEPTH_F32;
        break;
    default:
        throw Exception("");
    }

    return bitDepth;
}

Imf::PixelType bitDepthToPixelType(BitDepth bitDepth)
{
    Imf::PixelType pixelType;

    switch (bitDepth)
    {
    case BIT_DEPTH_F16:
        pixelType = Imf::HALF;
        break;
    case BIT_DEPTH_F32:
        pixelType = Imf::FLOAT;
        break;
    default:
        throw Exception("");
    }

    return pixelType;
}

size_t getPixelBytes(Imf::PixelType pixelType)
{
    size_t bytes;

    switch (pixelType)
    {
    case Imf::HALF:
        bytes = sizeof(half);
        break;
    case Imf::FLOAT:
        bytes = sizeof(float);
        break;
    default:
        throw Exception("");
    }

    return bytes;
}

size_t getPixelBytes(BitDepth bitDepth)
{
    size_t bytes;

    switch (bitDepth)
    {
    case BIT_DEPTH_UINT8:
        bytes = sizeof(uint8_t);
        break;
    case BIT_DEPTH_UINT10:
    case BIT_DEPTH_UINT12:
    case BIT_DEPTH_UINT14:
    case BIT_DEPTH_UINT16:
        bytes = sizeof(uint16_t);
        break;
    case BIT_DEPTH_F16:
        bytes = sizeof(half);
        break;
    case BIT_DEPTH_F32:
        bytes = sizeof(float);
        break;
    default:
        throw Exception("");
    }

    return bytes;
}

ImageInfo getExrImageInfo(const Imf::InputFile & file)
{
    ImageInfo info;

    Imf::Header header = file.header();

    Imath::Box2i dataWindow = header.dataWindow();
    info.x = dataWindow.min.x;
    info.y = dataWindow.min.y;
    info.width  = dataWindow.max.x - dataWindow.min.x + 1;
    info.height = dataWindow.max.y - dataWindow.min.y + 1;

    Imath::Box2i displayWindow = header.displayWindow();
    info.fullX = displayWindow.min.x;
    info.fullY = displayWindow.min.y;
    info.fullWidth  = displayWindow.max.x - displayWindow.min.x + 1;
    info.fullHeight = displayWindow.max.y - displayWindow.min.y + 1;

    Imf::ChannelList channels = header.channels();
    Imf::ChannelList::ConstIterator it = channels.begin();
    for (it; it != channels.end(); it++)
    {
        info.channelCount++;
        info.channels.push_back(
            { 
                it.name(), 
                pixelTypeToBitDepth(it.channel().type) 
            }
        );
    }

    return info;
}

ImageInfo getExrImageInfo(const std::string & filename)
{
    try
    {
        Imf::InputFile file(filename.c_str());
        return getExrImageInfo(file);
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }
}

bool readExr(const std::string & filename, 
             const std::vector<std::string> & channelNames, 
             BitDepth bitDepth, 
             void * pixels)
{
    bool ok = false;

    try
    {
        Imf::InputFile file(filename.c_str());
        ImageInfo info = getExrImageInfo(file);

        Imf::FrameBuffer frameBuffer;

        Imf::PixelType pixelType = bitDepthToPixelType(bitDepth);
        size_t pixelBytes = getPixelBytes(bitDepth);
        size_t xStride = pixelBytes * (size_t)info.channelCount;
        size_t yStride = (size_t)info.width * xStride;
        char * base = (char *)pixels - info.x * xStride - info.y * yStride;

        size_t channelOffset = 0;
        for (const auto & channelName : channelNames)
        {
            frameBuffer.insert(channelName,
                               Imf::Slice(pixelType, 
                                          base + channelOffset, 
                                          xStride, 
                                          yStride));
            channelOffset += pixelBytes;
        }

        file.setFrameBuffer(frameBuffer);
        file.readPixels(info.y, info.y + info.height - 1);
        ok = true;
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }

    return ok;
}

bool writeExr(const std::string & filename, 
              const ImageInfo & info,
              BitDepth bitDepth, 
              const void * pixels)
{
    bool ok = false;

    try
    {
        Imath::Box2i displayWindow(
            Imath::V2i(info.fullX, 
                       info.fullY), 
            Imath::V2i(info.fullX + info.fullWidth - 1, 
                       info.fullY + info.fullHeight - 1)
        );
        Imath::Box2i dataWindow(
            Imath::V2i(info.x, 
                       info.y), 
            Imath::V2i(info.x + info.width - 1, 
                       info.y + info.height - 1)
        );
        Imf::Header header(displayWindow, dataWindow);

        for (const auto & channel : info.channels)
        {
            header.channels().insert(
                channel.name, 
                Imf::Channel(bitDepthToPixelType(channel.bitDepth))
            );
        }

        Imf::OutputFile file(filename.c_str(), header);
        Imf::FrameBuffer frameBuffer;

        Imf::PixelType pixelType = bitDepthToPixelType(bitDepth);
        size_t pixelBytes = getPixelBytes(bitDepth);
        size_t xStride = pixelBytes * (size_t)info.channelCount;
        size_t yStride = (size_t)info.width * xStride;
        char * base = (char *)pixels - info.x * xStride - info.y * yStride;

        size_t channelOffset = 0;
        for (const auto & channel : info.channels)
        {
            frameBuffer.insert(channel.name,
                               Imf::Slice(pixelType, 
                                          base + channelOffset, 
                                          xStride, 
                                          yStride));
            channelOffset += pixelBytes;
        }

        file.setFrameBuffer(frameBuffer);
        file.writePixels(info.height);
        ok = true;
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }

    return ok;
}

} // namespace

ImageInfo GetImageInfo(const std::string & filename)
{
    return getExrImageInfo(filename);
}

bool ReadImage(const std::string & filename, 
               const std::vector<std::string> & channelNames, 
               BitDepth bitDepth, 
               void * pixels)
{
    return readExr(filename, channelNames, bitDepth, pixels);
}

bool WriteImage(const std::string & filename, 
                const ImageInfo & info,
                BitDepth bitDepth, 
                const void * pixels)
{
    return writeExr(filename, info, bitDepth, pixels);
}

} // namespace OCIO_NAMESPACE
