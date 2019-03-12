# 88_tools
Miscellaneious toolkit for TORK

## rosversionall

List all installed ROS package location and versions

Usage : `$ curl -sL https://goo.gl/Dj5BCp | bash`

Example

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

## ci_setup

### create_travis_setting.py

Before using this program, please `fork` the target repository.

This program create PullRequest to add travis setting file (.travis.yml)

Usage : `curl -sL https://raw.github.com/tork-a/88_tools/master/ci_setup/create_travis_settings.py | python - http://github.com/PR2/robot_self_filter`

This will create `add_travis` branch to your forked repository, add `travis.yml` file and create pull request.

### change_maintainer_name.sh

This program will change the maintainer name to `ROS Orphaned Package Maintainers`

Example:

```
$ git clone http://github.com/foo/robot_self_filter
$ cd robot_self_filter
$ git checkout add_travis
$ ~/88_tools/ci_setup/change_maintainer_name.sh
```
