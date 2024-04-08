# EXPERIMENTS

### test1

put three blocks in the bowl step by step.

1. ['brown block', 'blue block', 'gray block', 'pink block', 'yellow bowl'] 48s, exec10,  subtasks：10.
2. ['purple block', 'orange block', 'cyan block', 'brown block', 'cyan bowl'] 40.5s, 10, 10
3. ['orange block', 'pink block', 'yellow block', 'purple block', 'cyan bowl'] 26s, 3, 12

def put_three_blocks_in_the_bowl_step_by_step():
	def put_three_blocks_in_the_bowl_step_by_step():
		# Step 1
		find('orange block')
		pick('orange block')
		find('cyan bowl')
		place('cyan bowl')

    # Step 2
		find('pink block')
		pick('pink block')
		find('cyan bowl')
		place('cyan bowl')

    # Step 3
		find('yellow block')
		pick('yellow block')
		find('cyan bowl')
		place('cyan bowl')

4. ['green block', 'yellow block', 'blue block', 'purple block', 'cyan bowl'] 46s, 8, 10

```
def put_three_blocks_in_the_bowl_step_by_step():
    # 0: Find three blocks
    find('green block')
    find('blue block')
    find('yellow block')
  
    # 1: Pick the green block
    pick('green block')
  
    # 2: Find a bowl
    find('cyan bowl')
  
    # 3: Place the green block in the bowl
    place('cyan bowl')
  
    # 4: Pick the blue block
    pick('blue block')
  
    # 5: Place the blue block in the bowl
    place('cyan bowl')
  
    # 6: Pick the yellow block
    pick('yellow block')
  
    # 7: Place the yellow block in the bowl
    place('cyan bowl')
```

5. ['blue block', 'red block', 'orange block', 'gray block', 'gray bowl'] 27s, 3, 12

```
def put_three_blocks_in_the_bowl_step_by_step():
	# 1st Block
	find('blue block')
	pick('blue block')
	find('gray bowl')
	place('gray bowl')

	# 2nd Block
	find('red block')
	pick('red block')
	find('gray bowl')
	place('gray bowl')

	# 3rd Block
	find('orange block')
	pick('orange block')
	find('gray bowl')
	place('gray bowl')
```

1. Store two blocks in the bowl
   1. Taking time:  127.98521304130554
      exec_subtasks:  [6]
      total_steps:  [10]

```
def store_two_blocks_in_the_bowl():
	# 0: find a block
	find('pink block')
	# 1: Pick the block
	pick('pink block')

	# 2: find another block
	find('brown block')
	# 3: Pick the second block
	pick('brown block')

	# 4: find a bowl
	find('red bowl')
	# 5: put the blocks in the bowl
	place('red bowl')
```

2. Taking time:  37.35371255874634
   exec_subtasks:  [7]
   total_steps:  [7]
3. Taking time:  26.980857610702515
   exec_subtasks:  [7]
   total_steps:  [7]
4. Taking time:  22.401047468185425
   exec_subtasks:  [8]
   total_steps:  [8]
5. choose two blocks and put it in the bowl

   ['gray block', 'red block', 'purple block', 'brown block', 'brown bowl']

   Taking time:  233.58923172950745
   exec_subtasks:  [7]
   total_steps:  [17]

### test2

put each block into each bowl

6. ['green block', 'blue block', 'purple bowl', 'pink bowl']

Taking time:  21.181960582733154
exec_subtasks:  [3]
total_steps:  [8]

```
def put_each_block_into_each_bowl():
    # 0: find all blocks and all bowls
    find('green block')
    find('blue block')
    find('purple bowl')
    find('pink bowl')
    # 1: Pick the green block and place it in the purple bowl
    pick('green block')
    place('purple bowl')
    # 2: Pick the blue block and place it in the pink bowl
    pick('blue block')
    place('pink bowl')
```

7. classify blocks according to the color of the bowl

['gray block', 'brown block', 'brown bowl', 'gray bowl']

Taking time:  22.407469511032104
exec_subtasks:  [8]
total_steps:  [8]

8. put all blocks in a bowl

['gray block', 'blue block', 'orange bowl', 'green bowl']

    Taking time:  23.996994495391846
	exec_subtasks:  [6]
	total_steps:  [7]

9. put two blocks in a cool color bowl

['yellow block', 'blue block', 'gray block', 'orange bowl', 'pink bowl', 'purple bowl', 'yellow bowl']

Taking time:  273.0451958179474
exec_subtasks:  [4]
total_steps:  [16]

```
def put_two_blocks_in_a_cool_color_bowl():

	# 0: find two blocks
	find('yellow block')
	find('blue block')

	# 1: Pick the blocks
	pick('yellow block')
	pick('blue block')

	# 2: find a cool color bowl
	find('purple bowl')

	# 3: put the blocks in the bowl
	place('purple bowl')
```

10. put all warm color blocks in the green bowl

    Taking time:  51.66972327232361
    exec_subtasks:  [5]
    total_steps:  [11]

['yellow block', 'gray block', 'blue block', 'green bowl', 'cyan bowl', 'brown bowl', 'pink bowl']

```
def put_all_warm_color_blocks_in_the_green_bowl():
    # 0: find the warm color blocks
    find('yellow block')
    find('orange block')
    # 1: Pick the yellow block
    pick('yellow block')
    # 2: Put the yellow block in the green bowl
    place('green bowl')
    # 3: Pick the orange block
    pick('orange block')
    # 4: Put the orange block in the green bowl
    place('green bowl')
```

### test3

make only one bowl empty xxxxxxxxxxxxxxxxxxxxxxxxx

11. ['gray block', 'cyan block', 'pink bowl', 'green bowl', 'red bowl']

put blocks in bowls until only one bowl is empty
