#!/bin/bash

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 reposiotry_name patch_number"
    exit
fi

function echo_red {
    echo -e "\e[31m$@\e[0m"
}
function echo_green {
    echo -e "\e[32m$@\e[0m"
}

patch_repo=$1
patch_no=$2
patch_dir=${3:-/opt/ros/hydro/share}
patch_prefix=${4:-1}

echo_green ";; download patch file https://github.com/${patch_repo}/pull/${patch_no}.diff"
wget -O /tmp/$$.patch https://github.com/${patch_repo}/pull/${patch_no}.diff 2> /dev/null
echo -e "\e[33m"
cat /tmp/$$.patch
echo -e "\e[0m"
# theck if this is python module
sed -n '/diff --git a\/\(.*\)\/src\/\1\/.*\.py/{q1}' /tmp/$$.patch
if [ $? -eq 1 ]; then
    cd /opt/ros/hydro/lib/python2.7/dist-packages
    prefix=3
else
    cd ${patch_dir}
    prefix=${patch_prefix}
fi
echo_green "sudo patch -fN -p${prefix} < /tmp/$$.patch"
sudo patch --dry-run -fN -p${prefix} < /tmp/$$.patch
if [ $? -eq 1 ]; then
    sudo patch --dry-run -R -fN -p${prefix} < /tmp/$$.patch
    if [ $? -eq 1 ]; then
	echo_red "ERROR: failed to patch"
    else
	echo_green "This patch is already applied"
    fi
    exit
fi
read -p "Do you wish to apply ${patch_no}.patch [y/N]? " yn
case $yn in
    [Yy]* ) ;;
        * ) echo_red "ABORTED"; exit;;
esac

sudo patch -fN -p${prefix} < /tmp/$$.patch
echo_green "DONE";
#https://github.com/start-jsk/rtmros_hironx/pull/318