cmake_minimum_required(VERSION 2.8.3)
project(88_tools)
find_package(catkin REQUIRED COMPONENTS rostest)

add_rostest(test/hotfix.test)
