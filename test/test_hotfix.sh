#!/bin/bash
# Software License Agreement (BSD License)
#
# Copyright (c) 2016, Tokyo Opensource Robotics Kyokai Association (TORK)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Tokyo Opensource Robotics Kyokai Association. nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Use https://github.com/fkanehiro/hrpsys-base/pull/978 to apply patch(es).

set -x

# Install ROS, hrpsys.
sudo -E sh -c 'echo "deb $DEB_REPOSITORY `lsb_release -cs` main" > /etc/apt/sources.list.d/ros-latest.list'
# Common ROS install preparation
wget http://packages.ros.org/ros.key -O - | sudo apt-key add -
lsb_release -a
sudo apt-get update && sudo apt-get -qq install -y python-rosdep ros-indigo-hrpsys
sudo apt-get -qq purge ros-indigo-hrpsys  # The dependency should be fulfilled by now, so removing in order to use the specific versino.
cd $TRAVIS_BUILD_DIR && sudo dpkg -i ./test/ros-indigo-hrpsys_315.8.0-0trusty-20160201-040843-0800_amd64.deb || (echo 'hrpsys installation failed at ${TRAVIS_BUILD_DIR}. Exitting.' && exit 1); # Need to use un-patched veersion of hrpsys.

# Run hotfix script.
wget https://patch-diff.githubusercontent.com/raw/fkanehiro/hrpsys-base/pull/978.patch
yes | ./hotfixer/hot_fix.sh fkanehiro/hrpsys-base 978 /opt/ros/indigo/lib/python2.7/dist-packages/hrpsys 2 0

# Check if the necessary change was made.
if grep -q "if isConnected(outP, inP) == True and False" /opt/ros/indigo/lib/python2.7/dist-packages/hrpsys/rtm.py; then 
  echo 'Looks like patch failed.';
  exit 1;
else
  exit 0;
fi
