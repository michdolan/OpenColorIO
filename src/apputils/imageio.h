// SPDX-License-Identifier: BSD-3-Clause
// Copyright Contributors to the OpenColorIO Project.

#ifndef INCLUDED_OCIO_IMAGEIO_H
#define INCLUDED_OCIO_IMAGEIO_H

#include <map>
#include <string>
#include <vector>

#include "OpenEXR/ImfHeader.h"

#include "OpenColorIO.h"

namespace OCIO_NAMESPACE
{

class ImageIO
{
public:
    ImageIO() = default;
    ImageIO(const std::string & filename);
    ImageIO(long width, long height, 
            ChannelOrdering chanOrder, 
            BitDepth bitDepth);
    ImageIO(const ImageIO & img);

    ImageIO(ImageIO &&) = delete;

    Image & operator = (const ImageIO &) = delete;
    Image & operator = (ImageIO &&) noexcept;

    ~ImageIO();

    void allocate(long width, long height, 
                  ChannelOrdering chanOrder, 
                  BitDepth bitDepth);

    void write(const std::string & filename) const;
    
    PackedImageDesc & getImageDesc() const noexcept { return m_desc; }
    void * getData() const noexcept { return m_data; }

    long getWidth() const { return m_desc.getWidth(); }
    long getHeight() const { return m_desc.getHeight(); }
    long getNumChannels() const { return m_desc.getNumChannels(); }

    ChannelOrdering getChannelOrder() const { return m_desc.getChannelOrder(); }
    BitDepth getBitDepth() const { return m_desc.getBitDepth(); }

    const std::vector<std::string> getChannelNames() const;

    ptrdiff_t getChanStrideBytes() const { return m_desc.getChanStrideBytes(); }
    ptrdiff_t getXStrideBytes() const { return m_desc.getXStrideBytes(); }
    ptrdiff_t getYStrideBytes() const { return m_desc.getYStrideBytes(); }
    ptrdiff_t getImageBytes() const;

    Imf::Header & getHeader() const noexcept { return m_header; }
    const Imf::Header & getHeader() const noexcept { return m_header; }

private:
    Imf::Header m_header;
    PackedImageDesc m_desc;

    void * m_data = nullptr;
};

} // namespace OCIO_NAMESPACE

#endif // INCLUDED_OCIO_IMAGEIO_H
