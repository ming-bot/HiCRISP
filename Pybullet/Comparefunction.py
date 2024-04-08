import numpy as np
from motion_primitives import Motion_primitives
import re
import copy
from LM_request import SentLM_request
import time

robot_have = "none"

def decode_action(action, observation, env, obj_list):
    global robot_have
    motion = Motion_primitives(env, obj_list)
    action_name = action[0]

    try:
        if type(action[1]) is np.ndarray:
            if action_name == 'pick':
                motion.pick(action[1])
            elif action_name == 'place':
                motion.place(action[1])
            robot_have = "none"
            return True, "The action is legal"
    except:
        pass
    obj = ""
    for j in range(1, len(action) -1):
        obj += action[j] + " "
    obj += action[-1]

    if action_name == 'find':
        if obj not in obj_list:
            return False, "The scence doesn't have the object."
        else:
            observation[obj] = motion.locate(obj)
            return True, observation[obj]
    elif action_name == 'pick':
        if obj not in obj_list:
            return False, "The scence doesn't have the object."
        elif obj not in observation.keys():
            return False, "The robot should find the object first."
        elif not "none" in robot_have:
            return False, "The robot should place the object it has before picks another."
        else:
            motion.pick(observation[obj])
            robot_have = obj
            return True, "The action is legal."
    elif action_name == 'place':
        if obj not in obj_list:
            return False, "The scence doesn't have the object."
        elif obj not in observation.keys():
            return False, "The robot should find the object first."
        else:
            motion.place(observation[obj])
            robot_have = "none"
            return True, "The action is legal"
    elif action_name == 'Complete':
        return True, "The action is legal"
    else:
        return False, "Bad action."


def run_execution(args, env, obj_list, test_task, gen_plan, log_file):
    per_task_item = 1
    exec_list = []
    total_list = []

    ## parse plan into subgoals ##
    log_file.write(f"\n--Executing task: {test_task}--\n")
    log_file.write(f"Plan:  {gen_plan}\n\n")
    print(f"Executing: {test_task}\n")

    subgoals = {}
    sub_goals_list = []
    begin_flag = False
    for i in gen_plan.split('\n'):
        i = i.strip()
        if "def" in i:
            begin_flag = True
        elif begin_flag is False or len(i) < 1:
            continue
        else:
            if "#" in i:
                sg = i.split("#")[1]; sg = sg.strip()
                subgoals[sg] = []
                sub_goals_list.append(sg)
            else:
                try:
                    subgoals[sg].append(i)
                except:
                    subgoals[0].append(i)
    
    print(f"subgoals list:\n{sub_goals_list}\n")
    print(f"There are {len(subgoals)} subtask unit")

    for i in range(per_task_item):
        ## begin execution ##
        reach_subgoals = 0; total_steps = 0; subgoal_index = 0
        _ = env.reset(obj_list)
        observation = {"robot":[0,0,0]}
        # step = 1
        act = ""
        begin_time = time.time()

        for subgoal in sub_goals_list:
            for action in subgoals[subgoal]:
                # fixes needed for not getting stuck
                # if step > 10:
                #     break
                # 去掉重复语句
                if act == action:
                    continue
                else:
                    act = action

                ## parse next action
                action = action.split(')')[0]
                action = re.findall(r"\b[a-z]+", action)
                # print(action)
                action_code = "Executing action:"
                motion_name = ""
                for item in action:
                    motion_name += " " + item
                log_file.write(f"{action_code + motion_name}\n\n")
                print(action_code + motion_name)

                decodestate, decodeinfo = decode_action(action, observation, env, obj_list)
                log_file.write(f"{decodestate, decodeinfo}\n\n")
                print(f"\n{decodestate, decodeinfo}\n")
                
                if not decodestate and "Bad action" in decodeinfo:
                    continue
                
                # since above steps are not for env, following line go through the env
                total_steps += 1

                # Perception
                perception_info = input("Give your judgement:")
                # perception_info = "success"
                log_file.write(f"\n{perception_info}\n")

                if "fail" in perception_info:
                    print(f"perception message: {perception_info}\n")
                    FixState, fixstep = ErrorHandle(action, observation, perception_info, args, log_file, env, obj_list)

                    if FixState is True:
                        print(f"Succesfully handle the error, and achieve the goal.We use {fixstep} to fix the problem.")
                        log_file.write(f"Succesfully handle the error, and achieve the goal.We use {fixstep} step(s) to fix the problem.\n")
                        total_steps += fixstep
                    else:
                        total_steps += 10
                        print(f"Can't handle the error. Please regenerate the task list.\n")
                        log_file.write(f"Can't handle the error. Please regenerate the task list.\n")
                        continue
                else:
                    pass
            
            # Perception
            perception_info = input("Give your judgement:")
            # perception_info = "success"
            log_file.write(f"\n{perception_info}\n")

            if "fail" in perception_info:
                print(f"perception message: {perception_info}\n")
                FixState, fixstep = ErrorHandle(action, observation, perception_info, args, log_file, env, obj_list)

                if FixState is True:
                    print(f"Succesfully handle the error, and achieve the goal.We use {fixstep} to fix the problem.")
                    log_file.write(f"Succesfully handle the error, and achieve the goal.We use {fixstep} step(s) to fix the problem.\n")
                    total_steps += fixstep
                else:
                    total_steps += 10
                    print(f"Can't handle the error. Please regenerate the task list.\n")
                    log_file.write(f"Can't handle the error. Please regenerate the task list.\n")
                    continue
            else:
                pass
            
            subgoal_index += 1
            reach_subgoals += 1

            if subgoal == sub_goals_list[-1]:
                # Perception
                perception_info = input("Give your final judgement:")
                # perception_info = "success"
                log_file.write(f"\n{perception_info}\n")

                if "fail" in perception_info:
                    print(f"perception message: {perception_info}\n")
                    FixState, fixstep = ErrorHandle(['Complete', 'task'], observation, perception_info, args, log_file, env, obj_list)

                    if FixState is True:
                        print(f"Succesfully handle the error, and achieve the goal.We use {fixstep} to fix the problem.")
                        log_file.write(f"Succesfully handle the error, and achieve the goal.We use {fixstep} step(s) to fix the problem.\n")
                        total_steps += fixstep
                    else:
                        total_steps += 10
                        print(f"Can't handle the error. Please regenerate the task list.\n")
                        log_file.write(f"Can't handle the error. Please regenerate the task list.\n")
                        continue
                else:
                    pass

        end_time = time.time()
        print("Taking time: ", end_time - begin_time)

        exec_list.append(reach_subgoals)
        total_list.append(total_steps)

    return exec_list, total_list

# Error的prompt
examplefix = [
    {"role": "system", "content": "You are a senior robot code engineer"},
    {"role": "user", "content": "Here i give you some code format examples."},
    {"role": "user", "content" : "pick('blue block') fail, because the gripper is empty."},
    {"role": "assistant", "content" : "pick('blue block')"},
    {"role": "user", "content" : "place('yellow bowl') fail, because the gripper is empty."},
    {"role": "assistant", "content" : "pick('blue block')"},
    {"role": "user", "content" : "pick('yellow bowl') fail, because the block is not in that position."},
    {"role": "assistant", "content" : "find('blue block')"},
    {"role": "system", "content": f"You can only use one of these functions in a time: find <obj>, pick <obj>, place <obj>"},
    {"role": "system", "content": f"You can only replace above obj with objects that are :"}
            ]

def NLP_task(tasklist):
    task_str = tasklist[0] + "('"
    for j in range(1, len(tasklist) - 1):
        task_str += tasklist[j] + " "
    task_str += tasklist[-1] + "')"
    return task_str

# 失败的反馈机制
def ErrorHandle(goal, observation, failinfo, args, log_file, env, obj_list):
    examplefix[-1]["content"] = examplefix[-1]["content"] + str(obj_list)
    initprompt = examplefix

    fixstep = 0
    # fix action queue
    failinfolist = []
    fixgoal = []
    fixgoal.append(copy.copy(goal))
    failinfolist.append(copy.copy(failinfo))

    while len(failinfolist) > 0 and fixstep < 10:
        # fail prompt
        failprompt = NLP_task(fixgoal[-1]) + " " + failinfolist[-1]
        log_file.write(f"{failprompt}\n")

        # ask the LLM
        initprompt.append({"role": "user", "content": failprompt})
        text = SentLM_request(initprompt, 
                    args.gpt_version)
        initprompt.pop()

        # LLM's response
        print("FixAction: ", text)
        log_file.write(f"\nfix action is: {text}\n")

        fixaction = text.split(')')[0]
        fixaction = re.findall(r"\b[a-z]+", fixaction)
        # decode the response
        actstate, actinfo = decode_action(fixaction, observation, env, obj_list)
        log_file.write(f"\nFixact_result: {actstate, actinfo}\n")
        print(f"\nFixact_result: {actstate, actinfo}")

        if not actstate and "Bad action" in actinfo:
            continue
        
        fixstep += 1
        # perception
        perception_info = input("Give your judgement:")
        log_file.write(f"{perception_info}\n\n")

        log_file.write(f"\nFixAction_Return: {perception_info}\n")
        print(f"\nFixAction_Return: {perception_info}\n")

        if 'fail' in perception_info:
            failinfolist.append(copy.copy(perception_info))
            fixgoal.append(copy.copy(fixaction))
            continue
        # success
        else:
            while len(fixgoal) >= 1:
                # try last action
                log_file.write(f"\nTRYact:{fixgoal[-1]}\n")
                print(f"TRYact:{fixgoal[-1]}")

                TRYstate, info = decode_action(fixgoal[-1], observation, env, obj_list)
                log_file.write(f"\nTRYact_result: {TRYstate, info}\n")
                print(f"\nTRYact_result: {TRYstate, info}")

                perception_info = input("Give your judgement:")
                log_file.write(f"\n{perception_info}\n")

                if 'fail' in perception_info:
                    log_file.write(f"TRYact_result: {perception_info}\n")
                    print(f"TRYact_result: {perception_info}")
                    failinfolist[-1] = copy.copy(perception_info)
                    break
                else:
                    log_file.write(f"TRYact_state: Fix successfully\n")
                    failinfolist.pop()
                    fixgoal.pop()
    
    ACTION_FLAG = True if len(fixgoal) == 0 else False
    
    return ACTION_FLAG, fixstep