#!/usr/bin/env python

import numpy as np
import rospy
import tf.transformations
from geometry_msgs.msg import PointStamped


class SyntheticOdometry(object):
    def __init__(self):
        rospy.init_node('synthetic_odometry')
        self.broadcaster = tf.TransformBroadcaster()
        self.resolution = rospy.get_param('~resolution')
        self.prev_actual_pose = None
        self.odom_frame_id = rospy.get_param('~odom_frame_id')
        self.base_frame_id = rospy.get_param('~base_frame_id')
        self.noise_mu_x_meters = float(rospy.get_param('~noise_mu_x', default=0))
        self.noise_mu_y_meters = float(rospy.get_param('~noise_mu_y', default=0))
        self.noise_sigma_x_meters = float(rospy.get_param('~noise_sigma_x', default=0))
        self.noise_sigma_y_meters = float(rospy.get_param('~noise_sigma_y', default=0))
        rospy.Subscriber('/ugv_pose', PointStamped, self.pose_callback)

    def pose_callback(self, this_actual_pose):
        if self.prev_actual_pose is None:
            self.prev_actual_pose = this_actual_pose
            self.broadcast_values = (0, 0)
            self.broadcaster.sendTransform((0, 0, 0), tf.transformations.quaternion_from_euler(0, 0, 0), rospy.Time.now(),
                                           child=self.base_frame_id, parent=self.odom_frame_id)
            return
        actual_delta_x = this_actual_pose.point.x - self.prev_actual_pose.point.x
        actual_delta_y = this_actual_pose.point.y - self.prev_actual_pose.point.y
        if self.noise_mu_x_meters != 0 or self.noise_sigma_x_meters != 0:
            broadcast_delta_x = actual_delta_x * self.resolution + np.random.normal(self.noise_mu_x_meters, self.noise_sigma_x_meters)
        else:
            broadcast_delta_x = actual_delta_x * self.resolution
        if self.noise_mu_y_meters != 0 or self.noise_sigma_y_meters != 0:
            broadcast_delta_y = (actual_delta_y * self.resolution + np.random.normal(self.noise_mu_y_meters, self.noise_sigma_y_meters)) * (-1)
        else:
            broadcast_delta_y = (actual_delta_y * self.resolution) * (-1)
        self.broadcast_values = (self.broadcast_values[0] + broadcast_delta_x, self.broadcast_values[1] + broadcast_delta_y)
        self.broadcaster.sendTransform((self.broadcast_values[0], self.broadcast_values[1], 0), tf.transformations.quaternion_from_euler(0, 0, 0),
                                       rospy.Time.now(), child=self.base_frame_id, parent=self.odom_frame_id)
        self.prev_actual_pose = this_actual_pose


if __name__ == '__main__':
    SyntheticOdometry()
    rospy.spin()