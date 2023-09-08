import time
import random
import openai
import numpy as np
import time
import re
import os
import copy
import sys
import rospy
from geometry_msgs.msg import PoseStamped, Pose
from tf.transformations import quaternion_from_euler
from control import mycar
from astar import mymap

def ChatLM(message, gpt_version, max_tokens=128, temperature=0, stop=None, frequency_penalty=0):
    os.environ["http_proxy"] = "http://127.0.0.1:7890"
    os.environ["https_proxy"] = "http://127.0.0.1:7890"
    response = openai.ChatCompletion.create(model=gpt_version, 
                                        messages=message, 
                                        max_tokens=max_tokens, 
                                        temperature=temperature, 
                                        stop=stop,
                                        frequency_penalty = frequency_penalty)
    time.sleep(20)

    return response, response["choices"][0]["message"]["content"].strip()

Mycar = mycar()

# 从大模型给出的伪代码解析到原子语句（可执行动作）
def moveto(string):
    if string == 'Area1':
        targetpose = Pose()
        targetpose.position.x = 3.0
        targetpose.position.y = 3.0
    elif string == 'Area2':
        targetpose = Pose()
        targetpose.position.x = 3.0
        targetpose.position.y = -3.0
    elif string == 'Area3':
        targetpose = Pose()
        targetpose.position.x = -3.0
        targetpose.position.y = 0.0
    return Mycar.move_to_position(targetpose)

def avoidtrap(string):
    targetpose = Pose()
    if string == 'Area1':
        targetpose.position.x = 3.0
        targetpose.position.y = 3.0
    elif string == 'Area2':
        targetpose.position.x = 3.0
        targetpose.position.y = -3.0
    elif string == 'Area3':
        targetpose.position.x = -3.0
        targetpose.position.y = 0.0

    Mycar.locate_car()
    Map = mymap(Mycar.trap)
    road = Map.Astar(Mycar.car_pose.position.x, Mycar.car_pose.position.y, targetpose.position.x, targetpose.position.y)
    if(len(road)==0):
        return False
    flag = True
    for item in road:
        targetpose.position.x = item[0]
        targetpose.position.y = item[1]
        flag = Mycar.move_to_position(targetpose)
        if not flag:
            return False
        else:
            time.sleep(1)
        
    return True

def decode_action(action, detector, log_file):
    if len(action) == 2 and action[0] in ["moveto"]: # 1 obj action
        obj1 = action[1]
        log_file.write("moveto <{}>\n".format(obj1))
        print("moveto <{}>\n".format(obj1))
        actionflag = moveto(obj1)
        if actionflag:
            # Detector Give a message TODO:
            return detector.check(action[1])
        else:
            return False, "The Car faces some traps in the road.\n"
    elif len(action) == 2:
        obj1 = action[1]
        log_file.write("avoidtrap <{}>\n".format(obj1))
        print("avoidtrap <{}>\n".format(obj1))
        actionflag = avoidtrap(obj1)
        if not actionflag:
            return False, "The Car faces some traps in the road.\n"
        else:
            return True, ""
    else:
        log_file.write("bad action\n")
        print("bad action\n")
        return False, "Bad action"

# 检测plan顺序
class Detector():
    def __init__(self, task) -> None:
        self.order = re.findall(r"\b[0-9]+", task)
        self.index = 0
    
    def check(self, string : str):
        if self.index < len(self.order):
            if self.order[self.index] not in string:
                return False, "The Car should move to Area{} firstly.\n".format(self.order[self.index])
            else:
                self.index += 1
                return True, ""
        else:
            return True, "The task is done.\n"

# 主处理函数
def run_execution(args, test_tasks, gen_plan, log_file, init_prompt = None):
    exec_per_task = []

    for task, plan in zip(test_tasks, gen_plan):
        ## parse plan into subgoals ##
        log_file.write(f"\n--Executing task: {task}--\n")
        log_file.write(f"Plan:  {plan}\n\n")
        print(f"Executing: {task}\n")

        detector = Detector(task)

        subgoals = {}
        # subgoals['-1'] = []
        for i in plan.split('\n'):
            i = i.strip()
            if len(i) < 1 or "def" in i:
                continue
            else:
                if "#" in i:
                    sg = i.split("#")[1]; sg = sg.strip()
                    subgoals[sg] = []
                else:
                    subgoals[sg].append(i)
        
        print(f"subgoals list:\n{subgoals}\n")
        print(f"There are {len(subgoals)} subtask unit")

        ## begin execution ##
        executable_steps = 0; total_steps = 0

        statelist = list(subgoals.keys())
        steplist = np.arange(1, len(statelist))
        # print(steplist)

        modelsbuff = {}
        statesbuff = {}

        for subgoal in subgoals.keys():
            step = 1; act = ""
            for action in subgoals[subgoal]:
                # fixes needed for not getting stuck
                if step > 10:
                    break
                # 去掉重复语句
                if act == action:
                    continue
                else:
                    act = action

                # since above steps are not for env, following line go through the env
                total_steps += 1
                
                ## parse next action
                action = action.split(')')[0]
                action = re.findall(r"\b[a-z,A-Z,0-9]+", action)
                print(action)
                # print(modelsbuff)
                # print(statesbuff)
                actstate, actinfo = decode_action(action, detector, log_file)
                
                if not actstate:
                    log_file.write(f"act_state: {actstate}, message: {actinfo}\n")
                    print(f"act_state: {actstate}, message: {actinfo}\n")
                    if actinfo == "Bad action":
                        continue
                    # 执行失败了
                    FixState, fixstep = ErrorHandle(action, detector, actinfo, init_prompt, args, log_file)
                    if FixState is True:
                        print(f"Succesfully handle the error, and achieve the goal.We use {fixstep} to fix the problem.")
                        log_file.write(f"Succesfully handle the error, and achieve the goal.We use {fixstep} step(s) to fix the problem.\n")
                        step += fixstep
                    else:
                        print(f"Can't handle the error. Please regenerate the task list.\n")
                        log_file.write(f"Can't handle the error. Please regenerate the task list.\n")
                        continue

                # else:
                else:
                    log_file.write(f"act_state: {actstate}\n")
                    print(f"act_state: {actstate}\n")
                # count execution if action executes succesfully in graph env
                executable_steps += 1

        exec_per_task.append(executable_steps / total_steps)
    return exec_per_task

# Error的prompt
examplefix = [{"role": "user", "content" : "An error occurred while executing moveto('Area1').The error message is:The Car should move to Area2 firstly."},
            {"role": "assistant", "content" : "moveto('Area2')"},
            {"role": "user", "content" : "An error occurred while executing moveto('Area1').The error message is:.The Car faces some traps in the road."},
            {"role": "assistant", "content" : "avoidtrap('Area1')"},
            ]

def NLP_task(tasklist):
    task_str = tasklist[0] + "('"
    for j in range(1, len(tasklist) - 1):
        task_str += tasklist[j] + "', '"
    task_str += tasklist[-1] + "')"
    return task_str

# 失败的反馈机制
def ErrorHandle(goal, detector, failinfo, initprompt, args, log_file):
    # init prompt
    initprompt = initprompt.copy()
    initprompt.extend(examplefix)
    fixstep = 0
    # fix action queue
    failinfolist = []
    fixgoal = []
    fixgoal.append(copy.copy(goal))
    failinfolist.append(copy.copy(failinfo))

    while len(failinfolist) > 0 and fixstep < 5:
        # fail prompt
        failprompt = "An error occurred while executing " + NLP_task(fixgoal[-1]) + ".The error message is:" + failinfolist[-1]
        print(failprompt)
        # ask the LLM
        initprompt.append({"role": "user", "content": failprompt})
        _, text = ChatLM(initprompt, 
                    args.gpt_version, 
                    max_tokens=600,
                    stop='\n',
                    frequency_penalty=0.15)
        initprompt.pop()
        # LLM's response
        print("FixAction: ", text)

        fixaction = text.split(')')[0]
        fixaction = re.findall(r"\b[a-z,A-Z,0-9]+", fixaction)
        log_file.write(f"--------------------\n")
        print(f"--------------------\n")
        # decode the response
        actstate, actinfo = decode_action(fixaction, detector, log_file)
        # add this to the action list
        fixgoal.append(copy.copy(fixaction))

        log_file.write(f"--------------------\nFixAction_Return: {actstate}\n")
        print(f"--------------------\nFixAction_Return: {actstate}\n")
        fixstep += 1
        if actinfo == "Bad action":
            continue

        if not actstate:
            failinfolist.append(copy.copy(actinfo))
            continue
        else:
            while len(fixgoal) > 1:
                fixgoal.pop()
                # try last action
                log_file.write(f"TRYact:")
                print(f"TRYact:")
                TRYstate, info = decode_action(fixgoal[-1], detector, log_file)
                if not TRYstate:
                    log_file.write(f"TRYact_state: {TRYstate}, message: {info}\n")
                    print(f"TRYact_state: {TRYstate}, message: {info}\n")
                    failinfolist[-1] = copy.copy(info)
                    break
                else:
                    log_file.write(f"TRYact_state: {TRYstate}\n")
                    print(f"TRYact_state: {TRYstate}\n")
                    failinfolist.pop()
    
    ACTION_FLAG = True if len(fixgoal) == 1 else False
    
    return ACTION_FLAG, fixstep