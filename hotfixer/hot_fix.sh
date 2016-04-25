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
patch_dir=${3:-/opt/ros/indigo/share}
patch_prefix=${4:-1}
patch_index=${5:-1}

echo_green ";; download patch file https://github.com/${patch_repo}/pull/${patch_no}.diff"
wget -O /tmp/$$.patch -q --no-check-certificate https://github.com/${patch_repo}/pull/${patch_no}.diff || (echo_red "error on downloading pach files"; kill $$)
if [ ${patch_index} -ne -1 ]; then
    csplit -q -z /tmp/$$.patch --prefix /tmp/${patch_no}_$$_ --suffix-format='%d.patch' '/^diff/' {*}
    patch_file=/tmp/${patch_no}_$$_${patch_index}.patch
else
    patch_file=/tmp/$$.patch
fi
echo -e "\e[31mApply ${patch_file}\e[33m"
cat ${patch_file}
echo -e "\e[0m"

# theck if this is python module
sed -n '/diff --git a\/\(.*\)\/src\/\1\/.*\.py/{q1}' ${patch_file}
if [ $? -eq 1 ]; then
    cd /opt/ros/indigo/lib/python2.7/dist-packages
    prefix=3
else
    cd ${patch_dir}
    prefix=${patch_prefix}
fi
echo_green "running patch command at `pwd`"
echo_green "sudo patch -fN -p${prefix} < ${patch_file}"
sudo patch --dry-run -fN -p${prefix} < ${patch_file}
if [ $? -eq 1 ]; then
    sudo patch --dry-run -R -fN -p${prefix} < ${patch_file}
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

sudo patch -fN -p${prefix} < ${patch_file}
echo_green "DONE";
#https://github.com/start-jsk/rtmros_hironx/pull/318
