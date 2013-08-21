#!/usr/bin/env python
###############################################################################
# \file
#
# $Id:$
#
# Copyright (C) Brno University of Technology
#
# This file is part of software developed by dcgm-robotics@FIT group.
# 
# Author: Zdenek Materna (imaterna@fit.vutbr.cz)
# Supervised by: Michal Spanel (spanel@fit.vutbr.cz)
# Date: dd/mm/2012
#
# This file is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.
#

import roslib; roslib.load_manifest('rt_road_detection')
import rospy
from rt_road_detection.srv import getCorrectedWaypoint, getCorrectedWaypointRequest

import tf
from tf import TransformListener
from geometry_msgs.msg import PoseStamped

import actionlib
from actionlib_msgs.msg import *
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

def main():
    
  rospy.init_node('test_waypoint_corrector')

  
  tfl = TransformListener()
  
  rospy.sleep(1)
  
  srv = rospy.ServiceProxy('wp_corrector', getCorrectedWaypoint) 
  
  pose = PoseStamped()
  
  pose.header.frame_id = "base_link"
  pose.header.stamp = rospy.Time.now()
  
  pose.pose.position.x = 2
  pose.pose.position.y = 0
  pose.pose.position.z = 0
  
  pose.pose.orientation.x = 0
  pose.pose.orientation.y = 0
  pose.pose.orientation.z = 0
  pose.pose.orientation.w = 1
  
  tfl.waitForTransform(pose.header.frame_id,"odom",pose.header.stamp, rospy.Duration(5))
  
  pose = tfl.transformPose("odom", pose)
  
  req = getCorrectedWaypointRequest()
  
  req.wp_in.x = pose.pose.position.x
  req.wp_in.y = pose.pose.position.y
  
  print "REQ: " + str(req.wp_in.x) + " " + str(req.wp_in.y)
  
  resp = srv(req)
  
  print "RESP: " + str(resp.wp_out.x) + " " + str(resp.wp_out.y)
  
  rospy.sleep(2)
  
  move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
  
  rospy.loginfo("Waiting for move_base server")
  
  move_base.wait_for_server()
  
  goal = MoveBaseGoal()
  goal.target_pose.header.stamp = rospy.Time.now()
  goal.target_pose.header.frame_id = "odom"
  goal.target_pose.pose.position.x = resp.wp_out.x
  goal.target_pose.pose.position.y = resp.wp_out.y
  goal.target_pose.pose.position.z = 0
  
  #goal.target_pose.pose.orientation = pose.pose.orientation
  goal.target_pose.pose.orientation.x = 0
  goal.target_pose.pose.orientation.y = 0
  goal.target_pose.pose.orientation.z = 0
  goal.target_pose.pose.orientation.w = 1
  
  move_base.send_goal(goal)
  
  rospy.loginfo("Waiting for result.")
  
  move_base.wait_for_result()  
  
  rospy.loginfo("Finished.")
  
  state = move_base.get_state()
  
  if state == GoalStatus.SUCCEEDED:
      
      rospy.loginfo("SUCCEEDED")
      
  else:
      
      rospy.logwarn("Some error...")
  
  
if __name__ == '__main__':

  try:
      main()
  except rospy.ROSInterruptException: pass
