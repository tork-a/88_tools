#!/bin/bash

set -e

set -x
find -iname package.xml | xargs -n1 sed -i 's#<maintainer.*maintainer>#<maintainer email="ros-orphaned-packages@googlegroups.com">ROS Orphaned Package Maintainers</maintainer>#'
set +x

echo "# Changed the maintainer name"
git diff
echo ""
echo -n "Are you OK to commit? [y/n] "
read yn
case $yn in
    yes|y)
	set -x
	git commit -m "Change maintainer to ROS Orphaned Package Maintainers" -a
	set +x
	;;
    *)
	echo "Abort"
	exit 1
esac

exit 0


