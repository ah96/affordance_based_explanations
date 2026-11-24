"""
Starts the QSR service and the explanation node.

    ros2 launch affordance_based_explanations explanation.launch.py
    ros2 launch affordance_based_explanations explanation.launch.py \
        explanation_type:=suggestive task:="fetch a book"
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'explanation_type', default_value='counterfactual',
            description='descriptive, suggestive or counterfactual'),
        DeclareLaunchArgument(
            'task', default_value='',
            description='What the robot is doing, for example "fetch a book"'),
        DeclareLaunchArgument(
            'period', default_value='5.0',
            description='Seconds between two periodic explanations'),
        Node(
            package='affordance_based_explanations',
            executable='qsr_server.py',
            output='screen',
        ),
        Node(
            package='affordance_based_explanations',
            executable='explanation_node.py',
            output='screen',
            parameters=[{
                'explanation_type': ParameterValue(
                    LaunchConfiguration('explanation_type'), value_type=str),
                'task': ParameterValue(
                    LaunchConfiguration('task'), value_type=str),
                'period': ParameterValue(
                    LaunchConfiguration('period'), value_type=float),
            }],
        ),
    ])
