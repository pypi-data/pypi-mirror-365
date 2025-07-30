import numpy as np
from scipy.spatial.transform import Rotation

class vector3D():
    def __init__(self, val= (0, 0, 0)):
        """
        val -> [D1, D2, D3]
        """
        self.set(val)
        self.txt = ['D1', 'D2', 'D3']
    
    def set(self, val):
        self.D1 = val[0]
        self.D2 = val[1]
        self.D3 = val[2]
    
    def get(self) -> None:
        return np.array([self.D1, self.D2, self.D3]) 

    def get_round(self, dec= 2) -> None:
        return np.array([round(i, dec) for i in self.get()])
        
    def print(self, dec= 2, end= '\n'):
        txt = self.txt
        print(f'{txt[0]}: {round(self.D1, dec)}\n{txt[1]}: {round(self.D2, dec)}\n{txt[2]}: {round(self.D3, dec)}', end= end)
        

class orientation_rpy(vector3D):
    def __init__(self, oren= (0, 0, 0)):
        """
        oren -> [row, pitch, yaw]
        """
        self.set(oren)
        self.txt = 'RPY'
        
    def set(self, val):
        super().set(val)
        self.row, self.pitch, self.yaw = self.get()
        
    def get_deg(self, dec= 5):
        return np.array([round(np.degrees(i), dec) for i in self.get()])
    
    def set_ros2_geometry_msgs_quaternion(self, ros2_quat):
        r = Rotation.from_quat([ros2_quat.x, ros2_quat.y, ros2_quat.z, ros2_quat.w])
        self.set(r.as_euler('xyz'))


class cartesian_vector(vector3D):
    def __init__(self, val= (0, 0, 0)):
        """
        val -> [x, y, z]
        """
        self.set(val)
        self.txt = 'XYZ'
        
    def set(self, val, inc= False):
        if inc:
            val = np.array(val) + self.get()
        super().set(val)
        self.x, self.y, self.z = self.get()
        
    def rotate(self, oren):
        rotation = Rotation.from_euler('xyz', oren) 
        rotated_vector = rotation.apply(self.get())
        self.set(val= rotated_vector)
        
    def set_ros2_geometry_msgs_vector3(self, ros2_vector3):
        self.set((
            ros2_vector3.x,
            ros2_vector3.y,
            ros2_vector3.z
        ))
        

class IMU_acc(cartesian_vector):
    def __init__(self, acc= (0, 0, 0)):
        """
        val -> [x, y, z]
        """
        super().__init__(acc)
        self.g = 9.807
        
    def rotate(self, oren, neglect_gravity = False):
        super().rotate([oren[0], oren[1], 0])
        self.set([self.x, self.y, self.z - self.g * neglect_gravity])
        # self.set([self.x, self.y, 0])
