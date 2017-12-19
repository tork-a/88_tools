# 88_tools
Miscellaneious toolkit for TORK

## rosversionall

List all installed ROS package location and versions

Usage : `$ curl -sL https://goo.gl/Dj5BCp | bash`

Eample

```
$ source /opt/ros/kinetic/setup.bash
$ curl -sL https://goo.gl/Dj5BCp | bash
ROS_ROOT=/opt/ros/kinetic/share/ros
ROS_PACKAGE_PATH=/opt/ros/kinetic/share
ROS_MASTER_URI=http://localhost:11311
ROS_LOG_DIR=/home/tork/.ros/log/
ROSLISP_PACKAGE_DIRECTORIES=
ROS_DISTRO=kinetic
ROS_ETC_DIR=/opt/ros/kinetic/etc/ros
actionlib		1.11.9	/opt/ros/kinetic/share/actionlib
actionlib_msgs		1.12.5	/opt/ros/kinetic/share/actionlib_msgs

```

Note: Pleaes source `setup.bash` before run this program
