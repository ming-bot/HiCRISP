import numpy as np
import pandas as pd
import pymysql #需要预加装pip install PyMySQL
import time

a = np.zeros((1,45))
print(np.shape(a))
conn = pymysql.connect(host='192.168.139.18',user='ControlCommand',password='Erleng921010',db='robot_positions', autocommit=1)
cur = conn.cursor()
for i in range(10):
    cur.execute('select * from robot_pos_cam_all_long order by time desc limit 1')
    data = list(cur.fetchall()[0])
    print(data[0])
    print(data[25:28])
    time.sleep(0.01)
cur.close()