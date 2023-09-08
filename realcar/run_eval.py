import sys
import argparse
import os
import os.path as osp
import random
import glob
import openai
import json
import time

from utils_execute import *

def planner_executer(args):
    # define available actions and append available objects from the env
    prompt = []
    prompt.append({"role": "system", "content": "You are a senior robot code engineer"})
    prompt.append({"role": "system", "content": f"You can only use these functions: moveto <obj>, avoidtrap <obj>"})
    prompt.append({"role": "system", "content": f"You can only replace above obj with parameters in the following collection: \n\nobjects = Area1, Area2, Area3"})

    # load task examples
    with open(f"{args.progprompt_path}/data/pythonic_plans/train_complete_plan_set.json", 'r') as f:
        tmp = json.load(f)
        prompt_egs = {}
        for k, v in tmp.items():
            prompt_egs[k] = v
            prompt.append({"role": "user", "content": k})
            prompt.append({"role": "assistant", "content": v})

    # setup logging
    log_filename = f"{args.expt_name}_outputs"
    log_file = open(f"{args.progprompt_path}/results/{log_filename}_logs.txt", 'w')
    log_file.write(f"\n----PROMPT for planning----\n{prompt}\n")
    
    test_tasks = []
    with open(f"{args.progprompt_path}/data/test_file.json", 'r') as f:
        for line in f.readlines():
            test_tasks.append(list(json.loads(line).keys())[0])

    log_file.write(f"\n----Test set tasks----\n{test_tasks}\nTotal: {len(test_tasks)} tasks\n")

    # generate plans for the test set
    if not args.load_generated_plans:
        gen_plan = []
        for task in test_tasks:
            print(f"Generating plan for: {task}\n")
            prompt_task = "def {fxn}():".format(fxn = '_'.join(task.split(' ')))

            prompt.append({"role": "user", "content": prompt_task})
            _, text = ChatLM(prompt, 
                        args.gpt_version, 
                        stop=": Done",
                        max_tokens=600,  
                        frequency_penalty=0.15)
            prompt.pop()
            gen_plan.append(text + ":Done")

        # save generated plan
        line = {}
        print(f"Saving generated plan at: {log_filename}_plans.json\n")
        with open(f"{args.progprompt_path}/results/{log_filename}_plans.json", 'w') as f:
            for plan, task in zip(gen_plan, test_tasks):
                line[task] = plan
            json.dump(line, f)

    # load from file
    else:
        print(f"Loading generated plan from: {log_filename}.json\n")
        with open(f"{args.progprompt_path}/results/{log_filename}_plans.json", 'r') as f:
            data = json.load(f)
            test_tasks, gen_plan = [], []
            for k, v in data.items():
                test_tasks.append(k)
                gen_plan.append(v)

    # run execution
    print(f"\n----Runing execution----\n")
    exec_per_task = run_execution(args,
                                test_tasks, 
                                gen_plan,
                                log_file,
                                init_prompt = prompt)
    print("exec_per_task: ", exec_per_task)
    log_file.write(f"exec_per_task: {exec_per_task}\n")
    log_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--progprompt-path", type=str, default=r"/home/ming/Mecanum_ws/src/scripts")
    parser.add_argument("--expt-name", type=str, required=True)

    parser.add_argument("--openai-api-key", type=str, 
                        default="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")

    parser.add_argument("--gpt-version", type=str, default="gpt-3.5-turbo", 
                        choices=['gpt-3.5-turbo', 'gpt-3.5-turbo-0613', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo-16k-0613'])

    # parser.add_argument("--load-generated-plans", type=bool, default=False)
    parser.add_argument("--load-generated-plans", type=bool, default=True)
    
    args = parser.parse_args()
    openai.api_key = args.openai_api_key

    if not osp.isdir(f"{args.progprompt_path}/results/"):
        os.makedirs(f"{args.progprompt_path}/results/")

    planner_executer(args=args)