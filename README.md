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
