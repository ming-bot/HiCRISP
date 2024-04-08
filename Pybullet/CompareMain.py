import argparse
import os.path as osp
import os
import json
import time
from table_environment import *
from LM_request import SentLM_request
# from Comparefunction import run_execution
from hicrisp import run_execution

def planner_executer(args):
    #@title Initialize Env { vertical-output: true }
    high_resolution = False #@param {type:"boolean"}
    high_frame_rate = False #@param {type:"boolean"}

    # setup env and LMP
    env = PickPlaceEnv(render=True, high_res=high_resolution, high_frame_rate=high_frame_rate)
    obj_list = ['cyan block', 'gray block', 'pink block', 'brown block', 'red bowl']
    test_task = "Store two blocks in the bowl"
    _ = env.reset(obj_list)
    print(obj_list)

    # define available actions and append available objects from the env
    prompt = []
    prompt.append({"role": "system", "content": "You are a senior robot code engineer"})

    # load task examples
    with open(f"{args.project_path}/prompt_example/train_complete_plan_set.json", 'r') as f:
        tmp = json.load(f)
        prompt_egs = {}
        prompt.append({"role": "user", "content": "Here i give you some code format examples."})
        for k, v in tmp.items():
            prompt_egs[k] = v
            prompt.append({"role": "user", "content": k})
            prompt.append({"role": "assistant", "content": v})

    prompt.append({"role": "system", "content": f"You can only use these functions: find <obj>, pick <obj>, place <obj>, and the code should not be for/while structure."})
    prompt.append({"role": "system", "content": f"You can only replace above <obj> with objects that are :" + str(obj_list)})

    # setup logging
    log_filename = f"{args.expt_name}_outputs"
    log_file = open(f"{args.project_path}/compareresults/{log_filename}_logs.txt", 'w')
    log_file.write(f"\n----PROMPT for planning----\n{prompt}\n")

    log_file.write(f"\n----Test set tasks----\n{test_task}\n")

    # load plan for the test set
    with open(f"{args.project_path}/compareresults/plan.json", 'r') as f:
        data = json.load(f)
        gen_plan = data[test_task]

    # run execution
    print(f"\n----Runing execution----\n")
    exec, total = run_execution(args,
                                env, obj_list,
                                test_task, 
                                gen_plan,
                                log_file)

    print("exec_subtasks: ", exec)
    print("total_steps: ", total)
    log_file.write(f"exec_subtasks: {exec}\n")
    log_file.write(f"total_subtasks: {total}\n")
    log_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_path", type=str, default=".")
    parser.add_argument("--expt-name", type=str, required=True)

    parser.add_argument("--gpt-version", type=str, default="gpt-3.5-turbo", 
                        choices=['gpt-3.5-turbo', 'gpt-3.5-turbo-0613', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo-16k-0613'])
    
    args = parser.parse_args()

    if not osp.isdir(f"{args.project_path}/compareresults/"):
        os.makedirs(f"{args.project_path}/compareresults/")
    
    planner_executer(args)
