# HiCRISP
This is the code release for the paper : [HiCRISP: A Hierarchical Closed-Loop Robotic Intelligent Self-Correction Planner](http://arxiv.org/abs/2309.12089). It contains code for VisualHome simulation ( edited from [Progprompt](https://github.com/NVlabs/progprompt-vh) ) and Real AGV platform.



## Setup

We test our following system on windows11,  python3.9.12.

### 1. Establish environment

To obtain detailed instructions on how to download  [VirtualHome](https://github.com/xavierpuigf/virtualhome), you may refer to  [Progprompt](https://github.com/NVlabs/progprompt-vh).

### 2. Run VirtualHome experience

1. run the unity UI of VirualHome, it locates in 

   ```shell
   \virtualhome\src\virtualhome\simulation\unity_simulator\windows_exec.v2.3.0
   ```

   in my computer. Also you can change the arguments in the $run\_eval.py$ to open simulator automatically. 

2. run evaluation. Here is a minimal example how to run the evaluation script. Replace {arguments in curly braces} with appropriate values on your system:

   ```python
   python3 scripts/run_eval.py --expt-name {expt_name}
   ```

   We have fixed the majority of the parameters, and these parameters do not have a significant impact on validating the effectiveness of our framework. You can easily change them if you think it is important.

### 3. Run Real AGV experience

​	Regrettably, the connection to our remote physical platform in the laboratory is currently under development. However, we warmly welcome you to visit our laboratory in person to conduct experiments. We will make the source code open-source as a frame of reference, with the hope that it can assist you in deploying the next stage of work on a new robotic platform.



Note: Due to the limitations of the author's expertise, the code requires you to **modify the paths and undertake other necessary adjustments according to your system**. The overall portability aspect of the code could be improved, and we welcome any criticism and suggestions from everyone to help with its modification.
