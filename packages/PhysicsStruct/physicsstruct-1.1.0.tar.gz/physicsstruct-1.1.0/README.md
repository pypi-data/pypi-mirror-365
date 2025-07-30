# Physics Struct
A package containing set of classes for physics variables

## Example
<u>Create instance</u>, default value is (0, 0, 0)
```python
data = vector3D()
data2 = vector3D((1, 2, 3))
```

<u>Assign new value</u>, can be either list or tuple
```python
data.set([2, 2, 2])
```

<u>Get data</u>, the function will return a np.array()
- get_round() return a rounded value
- dec (optional): the decimal point can be specified, default value is 2
```python
data.get()
data.get_round()
data.get_round(dec= 5)
```

<u>Print value</u> of each dimension
- dec (optional): set the decimal point, default value is 2
- end (optional): same as 'end' parameter in a print() function
```
data.print()
data.pritn(dec= 3)
```

## Other Classes in the 3D vector space
```python
orientation = orientation_rpy()
# stored data in RPY as radian
# include .get_deg() which return the value in degree

velocity = cartesian_vector()
# stored data in XYZ
# include .rotate() to caluculate 3D Euler Rotation
# .set() include increment mode => .set(inc= True)

acc = IMU_acc()
# inherite cartesian_vector()
# .rotate() ignore yaw as IMU linear acceleration does
```

## ROS2 Implementation
Some classes contain a method to transfer data from ROS2 geometry_msgs <br>
**geometry_msgs/msg/Vector3** can be use with *cartesian_vector()*
```python
data = Vector3()
velocity.set_ros2_geometry_msgs_vector3(data)
```
**geometry_msgs/msg/Quaternion** can be use with *orientation_rpy()*
```python
data2 = Quaternion()
orientation.set_ros2_geometry_msgs_quaternion(data2)
```

