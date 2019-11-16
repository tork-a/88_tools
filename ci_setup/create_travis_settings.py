#!/usr/bin/python

## Portion of the code is copied from bloom/bloom/commands/release.py

# Software License Agreement (BSD License)
#
# Copyright (c) 2014, Open Source Robotics Foundation, Inc.
# Copyright (c) 2013, Willow Garage, Inc.
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
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
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

"""
this script create .travis.yml
"""

import argparse
import os
import re
import sys
import tempfile
import traceback

# python2/3 compatibility
try:
    from urllib.error import HTTPError, URLError
    from urllib.parse import urlparse
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import HTTPError, Request, URLError, urlopen
    from urlparse import urlparse
            
from bloom.logging import fmt, sanitize
from bloom.logging import info, warning, error
from bloom.logging import debug
from bloom.logging import get_error_prefix
from bloom.logging import get_success_prefix

_success = get_success_prefix()
_error = get_error_prefix()

from bloom.util import change_directory


from vcstools.vcs_abstraction import get_vcs_client

from bloom.commands.release import get_github_interface

import shutil

def write_travis_yaml():
    with open('.travis.yml', mode='w') as f:
        f.write('''
# this is .traivs.yml written by {0}

# https://github.com/ros-infrastructure/ros_buildfarm/blob/master/doc/jobs/devel_jobs.rst
# https://github.com/ros-infrastructure/ros_buildfarm/blob/master/doc/jobs/prerelease_jobs.rst
# while this doesn't require sudo we don't want to run within a Docker container
sudo: true
dist: trusty
language: python
python:
  - "3.4"
env:
  global:
    - JOB_PATH=/tmp/devel_job
    - ABORT_ON_TEST_FAILURE=1
  matrix:
    - ROS_DISTRO_NAME=kinetic OS_NAME=ubuntu OS_CODE_NAME=xenial ARCH=amd64
    - ROS_DISTRO_NAME=melodic OS_NAME=ubuntu OS_CODE_NAME=bionic ARCH=amd64
#   matrix:
#     allow_failures:
#       - env: ROS_DISTRO_NAME=kinetic OS_NAME=ubuntu OS_CODE_NAME=xenial ARCH=amd64
install:
  # either install the latest released version of ros_buildfarm
  - pip install ros_buildfarm
  # or checkout a specific branch
  #- git clone -b master https://github.com/ros-infrastructure/ros_buildfarm /tmp/ros_buildfarm
  #- pip install /tmp/ros_buildfarm
  # checkout catkin for catkin_test_results script
  - git clone https://github.com/ros/catkin /tmp/catkin
  # run devel job for a ROS repository with the same name as this repo
  - export REPOSITORY_NAME=`basename $TRAVIS_BUILD_DIR`
  # use the code already checked out by Travis
  - mkdir -p $JOB_PATH/ws/src
  - cp -R $TRAVIS_BUILD_DIR $JOB_PATH/ws/src/
  # generate the script to run a pre-release job for that target and repo
  - generate_prerelease_script.py https://raw.githubusercontent.com/ros-infrastructure/ros_buildfarm_config/production/index.yaml $ROS_DISTRO_NAME default $OS_NAME $OS_CODE_NAME $ARCH  --output-dir $JOB_PATH
  # run the actual job which involves Docker
  - cd $JOB_PATH; sh ./prerelease.sh -y
script:
  # get summary of test results
  - /tmp/catkin/bin/catkin_test_results $JOB_PATH/ws/test_results --all
notifications:
  email: false

'''.format(sys.argv[0]))

def write_readme_md(base_org, base_repo, base_branch, **kwargs):
    def _write_status(f, base_org, base_repo, base_branch, **kwargs):
        f.write('{base_repo} [![Build Status](https://travis-ci.com/{base_org}/{base_repo}.svg?branch={base_branch})](https://travis-ci.com/{base_org}/{base_repo})\n'.format(**locals()))

    def _write_line(f, base_org, base_repo, base_branch, **kwargs):
        f.write('{}\n'.format('='*(len(base_org)*2+len(base_repo)*3+len(base_branch)+80)))

    readme = 'README.md'
    if not os.path.exists(readme):
        with open('README.md', mode='w') as f:
            _write_status(**locals())
            _write_line(**locals())
    else:
        with open(readme) as from_file:
            line = from_file.readline()
            with open(readme+'bak', mode='w') as to_file:
                _write_status(to_file, **locals())
                line = from_file.readline()
                _write_line(to_file, **locals())
                # if 2nd line is not a line
                if not re.match("\s*=+\s*", line):
                    to_file.write(line)
                shutil.copyfileobj(from_file, to_file)
            shutil.copyfile(readme+'bak', readme)

def get_gh_info(url):
    o = urlparse(url)
    if 'github.com' not in o.netloc:
        return None, None
    url_paths = o.path.split('/')
    if len(url_paths) < 3:
        return None, None
    return url_paths[1], url_paths[2]

def open_pull_request(base_org, base_repo, base_branch, new_branch="add_travis", title="update travis.yml"):
    def _my_run(cmd, msg=None):
        if msg:
            info(fmt("@{bf}@!==> @|@!" + sanitize(msg)))
        else:
            info(fmt("@{bf}@!==> @|@!" + sanitize(str(cmd))))
        from subprocess import check_call
        check_call(cmd, shell=True)

    # get ghe github interface
    gh = get_github_interface()
    
    # if gh is None:
    #     return None
    head_org = gh.username  # The head org will always be gh user
    head_repo = None

    # Check if a fork already exists on the user's account
    repo_forks = gh.list_forks(base_org, base_repo)
    user_forks = [r for r in repo_forks if r.get('owner', {}).get('login', '') == gh.username]
    # github allows only 1 fork per org as far as I know. We just take the first one.
    head_repo = user_forks[0] if user_forks else None
    if head_repo is None:
        error("Could not find a fork of {base_org}/{base_repo} on the {gh.username} GitHub account."
                .format(**locals()))
        error("Please create fork repository manually", exit=True)
        return 1

    head_repo = head_repo.get('name', '')
    if new_branch in [x['name'] for x in gh.list_branches(head_org, head_repo)]:
        error("Please remove {new_branch} in {head_org}/{head_repo} manually".format(**locals()))
        return 1
    
    target_url = 'https://{gh.token}:x-oauth-basic@github.com/{base_org}/{base_repo}.git'.format(**locals())
    target_fork_url = 'https://{gh.token}:x-oauth-basic@github.com/{head_org}/{head_repo}.git'.format(**locals())

    _my_run('git --no-pager diff'.format(**locals()))
    
    _my_run('git checkout -b {new_branch}'.format(**locals()))
    _my_run('git add .travis.yml README.md'.format(**locals()))
    _my_run('git commit -m "{title}"'.format(**locals()))
    _my_run('git push {target_fork_url} {new_branch}'.format(**locals()), "Pushing changes to fork")

    # Open the pull request
    body = '''
Created travis.yml using
- https://github.com/ros-infrastructure/ros_buildfarm/blob/master/doc/jobs/devel_jobs.rst
- https://github.com/ros-infrastructure/ros_buildfarm/blob/master/doc/jobs/prerelease_jobs.rst

Please activate GitHub - TravisCI integration to enable this test
https://github.com/apps/travis-ci
'''
    info(fmt("@{bf}@!==> @|@!" +
             "Using this fork to make a pull request from: {head_org}/{head_repo}".format(**locals())))
    
    try:
        pull_request_url = gh.create_pull_request(base_org, base_repo, base_branch, head_org, new_branch, title, body)
        if pull_request_url:
            info(fmt(_success) + "Pull request opened at: {0}".format(pull_request_url))
        else:
            info("The release of your packages was successful, but the pull request failed.")
            info("Please manually open a pull request by editing the file here: '{0}'"
                 .format(get_distribution_file_url(distro)))
            info(fmt(_error) + "No pull request opened.")
    except Exception as e:
            debug(traceback.format_exc())
            error("Failed to open pull request: {0} - {1}".format(type(e).__name__, e), exit=True)
    return 0

def get_argument_parser():
    parser = argparse.ArgumentParser(description="Create .travis.yml for ROS packages")
    add = parser.add_argument
    add('repository', help="repository to add .travis.yml")
    add('--verbose', '-v', action='store_true', default=False, help="show debug message")
    return parser

def main(sysargs):
    parser = get_argument_parser()
    args = parser.parse_args(sys.argv[1:])
    repository = args.repository
    verbose = args.verbose

    # checkout target rpository
    info("Manually clone the repository")
    info("  git clone {0}".format(repository))
    git = get_vcs_client('git', tempfile.mktemp())
    info(fmt("@{gf}@!==> @|") +
             "Fetching repository from '{0}'".format(repository))
    ret = git.checkout(repository, verbose=verbose)
    if not ret:
        error("Could not checkout {}".format(repository))
        return 1

    # get the github repository info
    base_org, base_repo = get_gh_info(git.get_url())
    # get correct repo info (case sensitive)
    gh = get_github_interface()
    base_org, base_repo = get_gh_info(gh.get_repo(base_org, base_repo)['html_url'])

    base_branch = git.get_branches()[0] # is this ok?

    with change_directory(git.get_path()):
        # write travis yaml
        write_travis_yaml()
        # write readme
        write_readme_md(**locals())

        # create pull request
        open_pull_request(base_org=base_org, base_repo=base_repo, base_branch=base_branch, new_branch="add_travis")

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
