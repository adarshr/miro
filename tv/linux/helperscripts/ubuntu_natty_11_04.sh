#!/bin/bash

# This script installs dependencies for building and running Miro on
# Ubuntu 11.04 (Natty Narwhal).
#
# You run this sript AT YOUR OWN RISK.  Read through the whole thing
# before running it!
#
# This script must be run with sudo.

# Last updated:    March 9th, 2011
# Last updated by: Will Kahn-Greene

apt-get install \
    build-essential \
    git-core \
    pkg-config \
    python-pyrex \
    python-gtk2-dev \
    libwebkit-dev \
    libsoup2.4-dev

apt-get install \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libavahi-compat-libdnssd1 \
    libtorrent-rasterbar6 \
    python-libtorrent \
    libwebkitgtk-3.0-0 \
    python-webkit \
    python-gst0.10 \
    python-gconf \
    python-pycurl \
    python-mutagen \
    libboost1.42-dev \
    libtag1-dev \
    zlib1g-dev \
    gstreamer0.10-ffmpeg \
    gstreamer0.10-plugins-base \
    gstreamer0.10-plugins-good \
    gstreamer0.10-plugins-bad \
    gstreamer0.10-plugins-ugly \
    ffmpeg \
    ffmpeg2theora \
    libfaac0 \
    python-appindicator
    # libwebkit-1.0-2 \
