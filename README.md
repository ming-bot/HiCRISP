# ReflectionLLMrobot
拥有自我反思的LLM机器人



## 实验日记

#### 7.26 开始新的辛酸历程

##### 7.26 11点实验

ChatCompletion.create接口，上层命令为Bring the chips to the sofa，执行成功。参数如下：

```python
"--gpt-version", type=str, default="gpt-3.5-turbo-0613“
```

执行指令如下：

```python
<char0> [find] <chips> (328)
State check:
You see: chips, chips ON wallshelf.
assert('close' to 'chips')
True
<char0> [grab] <chips> (328)
<char0> [walk] <sofa> (368)
State check:
You see: chips, sofa ON rug.  You have chips.
assert('chips' in 'hands')
True
<char0> [puton] <chips> (328) <sofa> (368)
```

##### 7.26 13点实验

ChatCompletion.create接口，上层命令为测试集内容。0725文件。



#### 7.27实验日记

##### 7.27 14点实验

当assert假言gpt回答错误时，可能会导致后续执行操作的bug，即这里的PUTIN操作的失败：

```python
State check:
You see: salmon, .  You have salmon.
assert('salmon' in 'hands' )
False
<char0> [find] <salmon> (327)
Action: [FIND] <salmon> (327) [0], act_return: True
<char0> [grab] <salmon> (327)
Action: [GRAB] <salmon> (327) [0], act_return: True
State check:
You see: 
assert('close' to 'fridge' )
I'm
bad action
State check:
You see: 
assert('fridge' is 'opened' )
I'm
bad action
<char0> [putin] <salmon> (327) <fridge> (305)
Action: [PUTIN] <salmon> (327) <fridge> (305) [0], act_return: False
act_state: False, message: <character> (1) is not close to <fridge> (305) when executing "[PUTIN] <salmon> (327) <fridge> (305) [0]"
State check:
You see: 
assert('close' to 'fridge' )
I'm
bad action
State check:
You see: 
assert('fridge' is 'opened' )
I'm
bad action
<char0> [close] <fridge> (305)
Action: [CLOSE] <fridge> (305) [0], act_return: False
act_state: False, message: <character> (1) is not close to <fridge> (305) when executing "[PUTIN] <salmon> (327) <fridge> (305) [0]",<character> (1) is not close to <fridge> (305) when executing "[CLOSE] <fridge> (305) [0]"
```

将这失败信息重新输入GPT让它去生成解决方案，解决完再次尝试刚刚失败的动作，循环直到失败动作被修复。（有点类似单片机的异常处理）修复后的执行：

```python
State check:
You see: salmon, .  You have salmon.
assert('salmon' in 'hands' )
False
<char0> [find] <salmon> (327)
Action: [FIND] <salmon> (327) [0], act_return: True
<char0> [grab] <salmon> (327)
Action: [GRAB] <salmon> (327) [0], act_return: True
State check:
You see: 
assert('close' to 'fridge' )
I'm
bad action
State check:
You see: 
assert('fridge' is 'opened' )
I'm
bad action
<char0> [putin] <salmon> (327) <fridge> (305)
Action: [PUTIN] <salmon> (327) <fridge> (305) [0], act_return: False
act_state: False, message: <character> (1) is not close to <fridge> (305) when executing "[PUTIN] <salmon> (327) <fridge> (305) [0]"
<char0> [find] <fridge> (305)
FixAction: [FIND] <fridge> (305) [0], act_return: True
TRYact: [PUTIN] <salmon> (327) <fridge> (305) [0], TRYact_state: True
Succesfully handle the error, and achieve the goal.We use 1 to fix the problem.State check:
You see: 
assert('close' to 'fridge' )
I'm
bad action
State check:
You see: 
assert('fridge' is 'opened' )
I'm
bad action
<char0> [close] <fridge> (305)
Action: [CLOSE] <fridge> (305) [0], act_return: False
act_state: False, message: <character> (1) is not close to <fridge> (305) when executing "[CLOSE] <fridge> (305) [0]"
<char0> [find] <fridge> (305)
FixAction: [FIND] <fridge> (305) [0], act_return: True
TRYact: [CLOSE] <fridge> (305) [0], TRYact_state: True
Succesfully handle the error, and achieve the goal.We use 1 to fix the problem.
```
