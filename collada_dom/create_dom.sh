#!/bin/bash
set -x
set -e

TMPDIR=/tmp/tmp$$
mkdir -p $TMPDIR
cd $TMPDIR
[ -f collada-dom2.4-dp_2.4.3.0.orig.tar.gz ] || wget https://launchpad.net/~openrave/+archive/ubuntu/release/+files/collada-dom2.4-dp_2.4.3.0.orig.tar.gz
[ -f collada-dom2.4-dp_2.4.3.0-ubuntu1~trusty1.debian.tar.gz ] || wget https://launchpad.net/~openrave/+archive/ubuntu/release/+files/collada-dom2.4-dp_2.4.3.0-ubuntu1~trusty1.debian.tar.gz
rm -fr  collada-dom2.4-dp-2.4.3.0.orig
tar -xvzf collada-dom2.4-dp_2.4.3.0.orig.tar.gz
cd collada-dom2.4-dp-2.4.3.0.orig
tar -xvzf ../collada-dom2.4-dp_2.4.3.0-ubuntu1~trusty1.debian.tar.gz
wget https://patch-diff.githubusercontent.com/raw/rdiankov/collada-dom/pull/12.diff -O - | patch -p1
sed -i 's@2.4.3.0-ubuntu1~trusty1@2.4.3.99-ubuntu1~trusty1@' debian/changelog
dpkg-buildpackage -rfakeroot -uc -b
sudo dpkg -i ../*.deb

