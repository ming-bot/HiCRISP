import argparse
import os.path as osp
import os
import json
import time
from table_environment import *
from LM_request import SentLM_request
from hicrisp import run_execution

def planner_executer(args):
    #@title Initialize Env { vertical-output: true }
    num_blocks = 2 #@param {type:"slider", min:0, max:4, step:1}
    num_bowls = 3 #@param {type:"slider", min:0, max:4, step:1}
    high_resolution = False #@param {type:"boolean"}
    high_frame_rate = False #@param {type:"boolean"}

    # setup env and LMP
    env = PickPlaceEnv(render=True, high_res=high_resolution, high_frame_rate=high_frame_rate)
    block_list = np.random.choice(ALL_BLOCKS, size=num_blocks, replace=False).tolist()
    bowl_list = np.random.choice(ALL_BOWLS, size=num_bowls, replace=False).tolist()
    obj_list = block_list + bowl_list
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
    log_file = open(f"{args.project_path}/results/{log_filename}_logs.txt", 'w')
    log_file.write(f"\n----PROMPT for planning----\n{prompt}\n")
    
    test_task = input("Input task order: \n")

    log_file.write(f"\n----Test set tasks----\n{test_task}\n")

    # generate plans for the test set

    print(f"Generating plan for: {test_task}\n")
    prompt_task = "def {fxn}():".format(fxn = '_'.join(test_task.split(' ')))

    prompt.append({"role": "user", "content": prompt_task})
    gen_plan = SentLM_request(prompt, 
                args.gpt_version)

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
    parser.add_argument("--max_tokens", type=int, default=128)
    parser.add_argument("--temperature", type=int, default=0)
    parser.add_argument("--stop", type=bool, default=False)
    parser.add_argument("--frequency_penalty", type=int, default=0)
    
    args = parser.parse_args()

    if not osp.isdir(f"{args.project_path}/results/"):
        os.makedirs(f"{args.project_path}/results/")
    
    planner_executer(args)
