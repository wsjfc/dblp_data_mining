import pickle
import re
import itertools
import math
import numpy as np
import matplotlib.pyplot as plt
import json

with open('/dev/shm/pytmp2.txt', 'rb') as f:
    yearGroupDict = pickle.load(f)
f.close()

counter = np.zeros(9).reshape(3,3)

yearList = ['a', 'b', 'c', 'd']
for i in range(len(yearList) - 1):
    notChangeGroup = list()
    partionsChangedDict = dict()
    for j in yearGroupDict[yearList[i + 1]]:
        if j in yearGroupDict[yearList[i]]:
            counter[0,i] += 1
            notChangeGroup.append(j)
        else:
            lst = j.split(',')
            num = math.ceil(len(lst) / 2)
            subset = list(itertools.combinations(lst, num))

            for k in list(map(lambda x:re.findall('.*'+'.*'.join(x)+'.*','\n'.join(yearGroupDict[yearList[i]])), subset)):
                if k:
                    counter[1,i] += 1
                    partionsChangedDict[j] = [k for k in list(map(lambda x:re.findall('.*' + '.*'.join(x) + '.*', '\n'.join(yearGroupDict[yearList[i]])),
                                                                  subset)) if k][0]

                    break

    counter[2,i] = len(yearGroupDict[yearList[i + 1]]) - counter[0, i] - counter[1, i]
    with open(str(i)+'.json', 'w') as f:
        json.dump(partionsChangedDict, f)

    with open(str(i)+'.txt', 'w') as f:
        for name in notChangeGroup:
            f.write(name+'\n')

labels = ['Not Change','Portions Changed','Whole New']
titles = ['第一阶段到第二阶段','第二阶段到第三阶段','第三阶段到第四阶段']
exp = [0.1,0.0,0.0]
for i,title in zip(range(3),titles):
    plt.pie(x=counter[:,i].tolist(),labels = labels,autopct='%1.2f%%',explode=exp,startangle=90)
    plt.axis('equal')
    plt.title(title)
    plt.show()

