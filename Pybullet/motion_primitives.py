from table_environment import *

class Motion_primitives():
    def __init__(self, env_api, obj_list):
        self.env_API = env_api
        self.obj_list = obj_list
        self.motion_names = [
            'locate', 'pick', 'place'
        ]
    
    def check_vaild(self, motion):
        if motion not in self.motion_names:
            print("Illegal directives input!\n")
            return False
        return True
    
    def locate(self, name):
        if name not in self.obj_list:
            print("Items that do not exist in the scene!\n")
            return
        else:
            return self.env_API.get_obj_pos(name)
    
    def pick(self, pick_pos):
        hover_xyz = np.float32([pick_pos[0], pick_pos[1], 0.2])
        if pick_pos.shape[-1] == 2:
            pick_xyz = np.append(pick_pos, 0.025)
        else:
            pick_xyz = pick_pos
            pick_xyz[2] = 0.025

        # Move to object.
        ee_xyz = self.env_API.get_ee_pos()
        while np.linalg.norm(hover_xyz - ee_xyz) > 0.01:
            self.env_API.movep(hover_xyz)
            self.env_API.step_sim_and_render()
            ee_xyz = self.env_API.get_ee_pos()

        while np.linalg.norm(pick_xyz - ee_xyz) > 0.01:
            self.env_API.movep(pick_xyz)
            self.env_API.step_sim_and_render()
            ee_xyz = self.env_API.get_ee_pos()

        # Pick up object.
        self.env_API.gripper.activate()
        for _ in range(240):
            self.env_API.step_sim_and_render()
        while np.linalg.norm(hover_xyz - ee_xyz) > 0.01:
            self.env_API.movep(hover_xyz)
            self.env_API.step_sim_and_render()
            ee_xyz = self.env_API.get_ee_pos()

        for _ in range(50):
            self.env_API.step_sim_and_render()
        
        observation = self.env_API.get_observation()
        reward = self.env_API.get_reward()
        done = False
        info = {}
        return observation, reward, done, info

    def place(self, place_pos):
        if place_pos.shape[-1] == 2:
            place_xyz = np.append(place_pos, 0.15)
        else:
            place_xyz = place_pos
            place_xyz[2] = 0.15
        
        # Move to place location.
        ee_xyz = self.env_API.get_ee_pos()
        while np.linalg.norm(place_xyz - ee_xyz) > 0.01:
            self.env_API.movep(place_xyz)
            self.env_API.step_sim_and_render()
            ee_xyz = self.env_API.get_ee_pos()

        # Place down object.
        while (not self.env_API.gripper.detect_contact()) and (place_xyz[2] > 0.03):
            place_xyz[2] -= 0.001
            self.env_API.movep(place_xyz)
            for _ in range(3):
                self.env_API.step_sim_and_render()
        
        self.env_API.gripper.release()
        for _ in range(240):
            self.env_API.step_sim_and_render()
        place_xyz[2] = 0.2
        ee_xyz = self.env_API.get_ee_pos()
        while np.linalg.norm(place_xyz - ee_xyz) > 0.01:
            self.env_API.movep(place_xyz)
            self.env_API.step_sim_and_render()
            ee_xyz = self.env_API.get_ee_pos()
        place_xyz = np.float32([0, -0.5, 0.2])
        while np.linalg.norm(place_xyz - ee_xyz) > 0.01:
            self.env_API.movep(place_xyz)
            self.env_API.step_sim_and_render()
            ee_xyz = self.env_API.get_ee_pos()

        observation = self.env_API.get_observation()
        reward = self.env_API.get_reward()
        done = False
        info = {}
        return observation, reward, done, info