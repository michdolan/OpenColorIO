// SPDX-License-Identifier: BSD-3-Clause
// Copyright Contributors to the OpenColorIO Project.

#include <sstream>

#include "OpenEXR/half.h"
#include "OpenEXR/ImathBox.h"
#include "OpenEXR/ImfChannelList.h"
#include "OpenEXR/ImfFrameBuffer.h"
#include "OpenEXR/ImfInputFile.h"
#include "OpenEXR/ImfOutputFile.h"
#include "pystring/pystring.h"
#include "utils/StringUtils.h"

#include "imageio.h"

namespace OCIO_NAMESPACE
{

namespace
{

const std::vector<std::string> RgbaChans = { "R", "G", "B", "A" };
const std::vector<std::string> RgbChans  = { "R", "G", "B" };

std::vector<std::string> GetChannelNames(const ChannelOrdering & chanOrder)
{
    switch (chanOrder)
    {
        case CHANNEL_ORDERING_RGBA:
        case CHANNEL_ORDERING_BGRA:
        case CHANNEL_ORDERING_ABGR:
            return RgbaChans;
        case CHANNEL_ORDERING_RGB:
        case CHANNEL_ORDERING_BGR:
            return RgbChans;
    }

    std::stringstream ss;
    ss << "Error: Unsupported channel ordering: " << chanOrder;
    throw Exception(ss.str().c_str());
}

size_t GetNumChannels(const ChannelOrdering & chanOrder)
{
    switch (chanOrder)
    {
        case CHANNEL_ORDERING_RGBA:
        case CHANNEL_ORDERING_BGRA:
        case CHANNEL_ORDERING_ABGR:
            return 4;
        case CHANNEL_ORDERING_RGB:
        case CHANNEL_ORDERING_BGR:
            return 3;
    }

    std::stringstream ss;
    ss << "Error: Unsupported channel ordering: " << chanOrder;
    throw Exception(ss.str().c_str());
}

size_t BitDepthToBytes(const BitDepth & bitDepth)
{
    switch (bitDepth)
    {
        case BIT_DEPTH_F32:    return sizeof(float);
        case BIT_DEPTH_F16:    return sizeof(half);
        case BIT_DEPTH_UINT16: return sizeof(uint16_t);
        case BIT_DEPTH_UINT8:  return sizeof(uint8_t);
    }

    std::stringstream ss;
    ss << "Error: Unsupported bit-depth: " << BitDepthToString(bitDepth);
    throw Exception(ss.str().c_str());
}

void DeAllocateBuffer(void * & data)
{
    delete [](char*)data;
    data = nullptr;
}

void ReadOpenEXR(const std::string & filename, ImageIO & img)
{
    Imf::InputFile file(filename);

    const Imath::Box2i & dw = file.header().dataWindow();
    const long width  = (long)(dw.max.x - dw.min.x + 1);
    const long height = (long)(dw.max.y - dw.min.y + 1);

    const Imf::ChannelList & chanList = file.header().channels();

    // RGB channels are required at a minimum. If channels R, G, and B don't
    // exist, they will be created and zero filled.
    ChannelOrdering chanOrder = CHANNEL_ORDERING_RGB;

    // Use RGBA if channel A exists
    if (chanList.findChannel(RgbaChans[3]))
    {
        chanOrder = CHANNEL_ORDERING_RGBA;
    }

    // Start with the minimum supported bit-depth and increase to match the 
    // channel with the largest pixel type. UINT (mapping to BIT_DEPTH_UINT32) 
    // is unsupported.
    Imf::PixelType = Imf::HALF;
    BitDepth bitDepth = BIT_DEPTH_F16;

    for (const auto & name : RgbaChans)
    {
        Imf::Channel * chan = chanList.findChannel(name);
        if (chan && chan->type == Imf::FLOAT)
        {
            pixelType = Imf::FLOAT;
            bitDepth = BIT_DEPTH_F32;
            break;
        }
    }

    img.allocate(width, height, chanOrder, bitDepth);

    // Copy existing attributes
    Imf::Header::ConstIterator attrIt = file.header().begin();
    for (; attrIt != file.header().end(); attrIt++)
    {
        img.getHeader().insert(attrIt->name(), attrIt->attribute());
    }

    // Copy predefined attributes
    img.getHeader().dataWindow()         = dw;
    img.getHeader().displayWindow()      = file.header().displayWindow();
    img.getHeader().pixelAspectRatio()   = file.header().pixelAspectRatio();
    img.getHeader().screenWindowCenter() = file.header().screenWindowCenter();
    img.getHeader().screenWindowWidth()  = file.header().screenWindowWidth();
    img.getHeader().lineOrder()          = file.header().lineOrder();
    img.getHeader().compression()        = file.header().compression();

    // Channel names based on above allocated ChannelOrdering
    std::vector<std::string> chanNames = img.getChannelNames();

    // Read pixels into buffer
    const size_t x          = (size_t)dw.min.x;
    const size_t y          = (size_t)dw.min.y;
    const size_t chanStride = (size_t)img.getChanStrideBytes();
    const size_t xStride    = (size_t)img.getXStrideBytes();
    const size_t yStride    = (size_t)img.getYStrideBytes();

    Imf::FrameBuffer frameBuffer;

    for (size_t i = 0; i < chanNames.size(); i++)
    {
        frameBuffer.insert(
            chanNames[i],
            Imf::Slice(
                pixelType, 
                (char *)(img.getData() - x*xStride - y*yStride + i*chanStride),
                xStride, yStride, 
                1, 1, 
                // RGB default to 0.0, A default to 1.0
                (i == 3 ? 1.0 : 0.0)
            )
        );
    }

    file.setFrameBuffer(frameBuffer);
    file.readPixels(dw.min.y, dw.max.y);
}

void WriteOpenEXR(const std::string & filename, 
                  const ImageIO & img, 
                  const void * & buffer)
{
    const std::vector<std::string> chanNames = img.getChannelNames();
    const BitDepth bitDepth = img.getBitDepth();

    Imf::PixelType pixelType;

    if (bitDepth == BIT_DEPTH_F16)
    {
        pixelType = Imf::HALF;
    }
    else if (bitDepth == BIT_DEPTH_F32)
    {
        pixelType = Imf::FLOAT;
    }
    else
    {
        std::stringstream ss;
        ss << "Error: Bit-depth " 
           << BitDepthToString(bitDepth) 
           << " does not map to a supported OpenEXR pixel type";
        throw Exception(ss.str().c_str());
    }

    Imf::Header header(img.getHeader());

    for (const auto & name : chanNames)
    {
        header.channels().insert(name, Imf::Channel(pixelType));
    }

    Imf::OutputFile file(filename.c_str(), header);

    const Imath::Box2i & dw = header.dataWindow();
    const size_t x          = (size_t)dw.min.x;
    const size_t y          = (size_t)dw.min.y;
    const size_t chanStride = (size_t)img.getChanStrideBytes();
    const size_t xStride    = (size_t)img.getXStrideBytes();
    const size_t yStride    = (size_t)img.getYStrideBytes();

    Imf::FrameBuffer frameBuffer;

    for (size_t i = 0; i < chanNames.size(); i++)
    {
        frameBuffer.insert(
            chanNames[i],
            Imf::Slice(
                pixelType, 
                (char *)(img.getData() - x*xStride - y*yStride + i*chanStride),
                xStride, yStride, 
                1, 1, 
                // RGB default to 0.0, A default to 1.0
                (i == 3 ? 1.0 : 0.0)
            )
        );
    }

    file.setFrameBuffer(frameBuffer);
    file.writePixels(img.getHeight());
}

} // namespace

ImageIO::ImageIO(const std::string & filename)
{
    std::string root, ext;
    pystring::path::splitext(root, ext, filename);

    if (StringUtils::Compare(ext.c_str(), ".exr"))
    {
        ReadOpenEXR(filename, this);
    }
    else
    {
        std::stringstream ss;
        ss << "Error: Unsupported image file format: " << ext;
        throw Exception(ss.str().c_str());
    }
}

ImageIO::ImageIO(long width, long height, 
                 ChannelOrdering chanOrder, 
                 BitDepth bitDepth)
{
    allocate(width, height, chanOrder, bitDepth);
}

ImageIO::ImageIO(const ImageIO & img)
{
    allocate(img.getWidth(), img.getHeight(), 
             img.getChannelOrder(), 
             img.getBitDepth());
    memcpy(m_data, img.m_data, img.getImageBytes());
}

ImageIO::~ImageIO()
{
    if (m_data != nullptr)
    {
        DeAllocateBuffer(m_data);
        m_data = nullptr;
    }
}

ImageIO & ImageIO::operator= (ImageIO && img) noexcept
{
    if(this != &img)
    {
        DeAllocateBuffer(m_data);

        m_header = img.m_header;
        m_desc   = img.m_desc;
        m_data   = img.m_data;

        img.m_data = nullptr;
    }

    return *this;
}

void ImageIO::allocate(long width, long height, 
                       ChannelOrdering chanOrder, 
                       BitDepth bitDepth)
{
    if (m_data != nullptr)
    {
        DeAllocateBuffer(m_data);
    }

    const size_t numChans = GetNumChannels(chanOrder);
    const size_t bitDepthBytes = BitDepthToBytes(bitDepth);
    const size_t imgSizeInChars = bitDepthBytes * numChans * (size_t)(width * height);
    
    m_data = (void *)new char[imgSizeInChars];

    const ptrdiff_t chanStrideBytes = (ptrdiff_t)bitDepthBytes;
    const ptrdiff_t xStrideBytes    = (ptrdiff_t)numChans * chanStrideBytes;
    const ptrdiff_t yStrideBytes    = (ptrdiff_t)height * xStrideBytes;

    m_desc = PackedImageDesc(
        m_data,
        width, height,
        chanOrder,
        bitDepth,
        chanStrideBytes,
        xStrideBytes,
        yStrideBytes
    );

    m_header.dataWindow().min.x = 0;
    m_header.dataWindow().min.y = 0;
    m_header.dataWindow().max.x = (int)width;
    m_header.dataWindow().max.y = (int)height;

    m_header.displayWindow().min.x = 0;
    m_header.displayWindow().min.y = 0;
    m_header.displayWindow().max.x = (int)width;
    m_header.displayWindow().max.y = (int)height;
}

void ImageIO::write(const std::string & filename) const
{
    std::string root, ext;
    pystring::path::splitext(root, ext, filename);

    if (StringUtils::Compare(ext.c_str(), ".exr"))
    {
        WriteOpenEXR(filename, this);
    }
    else
    {
        std::stringstream ss;
        ss << "Error: Unsupported image file format: " << ext;
        throw Exception(ss.str().c_str());
    }
}

const std::vector<std::string> ImageIO::getChannelNames() const
{
    if (m_desc.getNumChannels() == 3)
    {
        return RgbChans;
    }
    else
    {
        return RgbaChans;
    }
}

ptrdiff_t ImageIO::getImageBytes() const
{
    return m_desc.getYStrideBytes() * (ptrdiff_t)(m_desc.getHeight());
}

} // namespace OCIO_NAMESPACE
