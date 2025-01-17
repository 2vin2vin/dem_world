import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
#	world_file = '/home/sohithvulipe/dem_world/volcano.world'
	#print(PathJoinSubstitution[FindPackageShare('dhira'), "worlds","volcano.world"])
	print(get_package_share_directory('dhira'))
	world_file = os.path.join(get_package_share_directory('dhira'), "worlds","volcano.world")
	print(world_file)
	use_sim_time = True

	robot_base = os.getenv('LINOROBOT2_BASE')
	
	ekf_config_path = PathJoinSubstitution([FindPackageShare("linorobot2_base"), "config", "ekf.yaml"])

	urdf_path = PathJoinSubstitution([FindPackageShare("linorobot2_description"), "urdf/robots", f"{robot_base}.urdf.xacro"])

	return LaunchDescription([
	    DeclareLaunchArgument('world', default_value=world_file, description='Path to world file'),
	    LogInfo(msg="Launching Gazebo world: " + world_file),
	    
	    DeclareLaunchArgument(name='urdf',default_value=urdf_path,description='URDF Path'),
	    DeclareLaunchArgument(name='use_sim_time',default_value='true',description='Simulation time'),
	    DeclareLaunchArgument(name='spawn_x',default_value='-5.0',description='Robot spawn position in X axis'),
	    DeclareLaunchArgument(name='spawn_y',default_value='5.0',description='Robot spawn position in Y axis'),
	    DeclareLaunchArgument(name='spawn_z',default_value='50.0',description='Robot spawn position in Z axis'),
	    DeclareLaunchArgument(name='spawn_yaw', default_value='0.0',description='Robot spawn heading'),

	    # Launch the Gazebo ROS node with the specified world file
	    ExecuteProcess(
		cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so',  '-s', 'libgazebo_ros_init.so', LaunchConfiguration('world')],
		output='screen'
	    ),
	    
	    Node(package='robot_state_publisher',
	    executable='robot_state_publisher',
	    name='robot_state_publisher',
	    output='screen',
	    parameters=[
	    {'use_sim_time': LaunchConfiguration('use_sim_time'),
	    'robot_description': Command(['xacro ', LaunchConfiguration('urdf')])}
	    ]
	    ),
	    Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time}, 
                ekf_config_path
            ],
            remappings=[("odometry/filtered", "odom")]
            ),


	    # Spawn the wheeler_description model in Gazebo
	    Node(
		package='gazebo_ros',
		executable='spawn_entity.py',
		name='spawn_model',
		arguments=['-entity', 'linorobot2','-topic','robot_description',
		'-x', LaunchConfiguration('spawn_x'),
                '-y', LaunchConfiguration('spawn_y'),
                '-z', LaunchConfiguration('spawn_z'),
                '-Y', LaunchConfiguration('spawn_yaw'),
            ],
		output='screen'
	    ),

	    # Log information about the launch
	    LogInfo(
		msg="Launching the Gazebo world and model along with static transform and fake joint calibration."
	    ),
	])

