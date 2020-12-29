import pygame        #导入pygame游戏模块
import time
import sys
import random
import numpy as np #导入numpy库
from pygame.locals import *

initChessList = []          #保存的是棋盘坐标
initRole = 2                #1：代表白棋； 2：代表黑棋
resultFlag = 0              #结果标志

broadHumScore = np.zeros((15,15))
broadComScore = np.zeros((15,15))

cacheHumScore = np.zeros((4,15,15)) #临时缓存，记录四个方向的分数
cacheComScore = np.zeros((4,15,15))


debug = False

screen = None
blackStorn = None
whiteStorn = None
ABcut = 0

class StornPoint():
    def __init__(self,x,y,value):
        '''
        :param x: 代表x轴坐标
        :param y: 代表y轴坐标
        :param value: 当前坐标点的棋子：0:没有棋子 1:白子 2:黑子
        '''
        self.x = x            #初始化成员变量
        self.y = y
        self.value = value

lastP = StornPoint(-1, -1, -1)

class SimplePoint():
    def __init__(self,x,y):
        '''
        :param x: 代表x轴坐标
        :param y: 代表y轴坐标
        '''
        self.x = x            #初始化成员变量
        self.y = y

def initChessSquare(x,y):     #初始化棋盘
    for i in range(15):       # 每一行的交叉点坐标
        rowlist = []
        for j in range(15):   # 每一列的交叉点坐标
            pointX = x+ j*40
            pointY = y+ i*40
            sp = StornPoint(pointX,pointY,0)
            rowlist.append(sp)
        initChessList.append(rowlist)

def coverToRealXY(x, y):     #坐标转换
    return 27 + x*40, 27 + y*40 

def judgeResult(i,j,value):   #横向判断
    global resultFlag
    flag = False
    for  x in  range(j - 4, j + 5):  # 横向有没有出现5连（在边缘依次逐一遍历，是否五个棋子的类型一样）
        if x >= 0 and x + 4 < 15 :
            if initChessList[i][x].value == value and \
                initChessList[i][x + 1].value == value and \
                initChessList[i][x + 2].value == value and \
                initChessList[i][x + 3].value == value and \
                initChessList[i][x + 4].value == value :
                flag = True
                break
                pass
    for x in range(i - 4, i + 5):  # 纵向有没有出现5连（在边缘依次逐一遍历，是否五个棋子的类型一样）
        if x >= 0 and x + 4 < 15:
            if initChessList[x][j].value == value and \
                    initChessList[x + 1][j].value == value and \
                    initChessList[x + 2][j].value == value and \
                    initChessList[x + 3][j].value == value and \
                    initChessList[x + 4][j].value == value:
                flag = True
                break
                pass

    # 先判断东北方向的对角下输赢 x 列轴， y是行轴 ， i 是行 j 是列（右斜向）（在边缘依次逐一遍历，是否五个棋子的类型一样）
    for x, y in zip(range(j + 4, j - 5, -1), range(i - 4, i + 5)):
        if x >= 0 and x + 4 < 15 and y + 4 >= 0 and y < 15:
            if initChessList[y][x].value == value and \
                    initChessList[y - 1][x + 1].value == value and \
                    initChessList[y - 2][x + 2].value == value and \
                    initChessList[y - 3][x + 3].value == value and \
                    initChessList[y - 4][x + 4].value == value:
                flag = True

    # 2、判断西北方向的对角下输赢 x 列轴， y是行轴 ， i 是行 j 是列（左斜向）（在边缘依次逐一遍历，是否五个棋子的类型一样）
    for x, y in zip(range(j - 4, j + 5), range(i - 4, i + 5)):
        if x >= 0 and x + 4 < 15 and y >= 0 and y + 4 < 15:
            if initChessList[y][x].value == value and \
                    initChessList[y + 1][x + 1].value == value and \
                    initChessList[y + 2][x + 2].value == value and \
                    initChessList[y + 3][x + 3].value == value and \
                    initChessList[y + 4][x + 4].value == value:
                flag = True


    return flag

def getScoreWithPoint(x,y,value,dir):   #判断分数
    count1 = 1
    count2 = 0
    enemyNum = 0
    empty = -1
    result = 0
    # s = "count1 " + str(count1) + " count2 " + str(count2) + " x " + str(x) + " enemyNum " + str(enemyNum) + " empty " + str(empty) + " result " + str(result)
    # print(s)

    if dir == -1 or dir == 0:
        i = y
        while True:
            i += 1
            if i >= 15:
                enemyNum += 1
                break
            t = initChessList[x][i]
            if t.value == 0:
                if empty == -1 and i < 14 and initChessList[x][i + 1].value == value:
                    empty = count1
                    continue
                else:
                    break
            if t.value == value:
                count1 += 1
                continue
            else:
                enemyNum += 1
                break
        
        i = y
        while True:
            i -= 1
            if i < 0:
                enemyNum += 1
                break
            t = initChessList[x][i]
            if t.value == 0:
                if empty == -1 and i > 0 and initChessList[x][i - 1].value == value:
                    empty = 0 #这里的参数自己搞一搞
                    continue
                else:
                    break
            if t.value == value:
                count2 += 1
                if empty != -1:
                    empty += 1
                continue
            else:
                enemyNum += 1
                break
        if debug:
            print('- - - count:')    
            print(count1 + count2)
        
        score = countToScore(count1 + count2, enemyNum, empty)
        if value == 1:
            cacheComScore[0][x][y] = score
        elif value == 2:
            cacheHumScore[0][x][y] = score
        result += score

    count1 = 1
    count2 = 0
    enemyNum = 0
    empty = -1

    if dir == -1 or dir == 1:
        i = x
        while True:
            i += 1
            if i >= 15:
                enemyNum += 1
                break
            t = initChessList[i][y]
            if t.value == 0:
                if empty == -1 and i < 14 and initChessList[i + 1][y].value == value:
                    empty = count1
                    continue
                else:
                    break
            if t.value == value:
                count1 += 1
                continue
            else:
                enemyNum += 1
                break
        
        i = x
        while True:
            i -= 1
            if i < 0:
                enemyNum += 1
                break
            t = initChessList[i][y]
            if t.value == 0:
                if empty == -1 and i > 0 and initChessList[i - 1][y].value == value:
                    empty = 0 #这里的参数自己搞一搞
                    continue
                else:
                    break
            if t.value == value:
                count2 += 1
                if empty != -1:
                    empty += 1 
                continue
            else:
                enemyNum += 1
                break
        if debug:
            print('| | | count:')    
            print(count1 + count2)

        score = countToScore(count1 + count2, enemyNum, empty)
        if value == 1:
            cacheComScore[1][x][y] = score
        elif value == 2:
            cacheHumScore[1][x][y] = score
        result += score

    count1 = 1
    count2 = 0
    enemyNum = 0
    empty = -1

    if dir == -1 or dir == 2:
        i = x
        j = y
        while True:
            i += 1
            j += 1
            if i >= 15 or j >= 15:
                enemyNum += 1
                break
            t = initChessList[i][j]
            if t.value == 0:
                if empty == -1 and i < 14 and j < 14 and initChessList[i + 1][j + 1].value == value:
                    empty = count1
                    continue
                else:
                    break
            if t.value == value:
                count1 += 1
                continue
            else:
                enemyNum += 1
                break
        
        i = x
        j = y
        while True:
            i -= 1
            j -= 1
            if i < 0 or j < 0:
                enemyNum += 1
                break
            t = initChessList[i][j]
            if t.value == 0:
                if empty == -1 and i > 0 and j > 0 and initChessList[i - 1][j - 1].value == value:
                    empty = 0 #反过来数了，初始为0（算上必有的棋子，位置应该是1）
                    continue
                else:
                    break
            if t.value == value:
                count2 += 1
                if empty != -1:
                    empty += 1 #左边多了相同棋子，empty的位置向后顺延
                continue
            else:
                enemyNum += 1
                break
        if debug:
            print('\ \ \ count:')    
            print(count1 + count2)
        score = countToScore(count1 + count2, enemyNum, empty)
        if value == 1:
            cacheComScore[2][x][y] = score
        elif value == 2:
            cacheHumScore[2][x][y] = score
        result += score

    count1 = 1
    count2 = 0
    enemyNum = 0
    empty = -1

    if dir == -1 or dir == 3:
        i = x
        j = y
        while True:
            i += 1
            j -= 1
            if i >= 15 or j < 0:
                enemyNum += 1
                break
            t = initChessList[i][j]
            if t.value == 0:
                if empty == -1 and i < 14 and j > 0 and initChessList[i + 1][j - 1].value == value:
                    empty = count1
                    continue
                else:
                    break
            if t.value == value:
                count1 += 1
                continue
            else:
                enemyNum += 1
                break
        
        i = x
        j = y
        while True:
            i -= 1
            j += 1
            if i < 0 or j >= 15:
                enemyNum += 1
                break
            t = initChessList[i][j]
            if t.value == 0:
                if empty == -1 and i > 0 and j < 14 and initChessList[i - 1][j + 1].value == value:
                    empty = 0 
                    continue
                else:
                    break
            if t.value == value:
                count2 += 1
                if empty != -1:
                    empty += 1 
                continue
            else:
                enemyNum += 1
                break
        
        if debug:
            print('/ / / count:')    
            print(count1 + count2)
        score = countToScore(count1 + count2, enemyNum, empty)
        if value == 1:
            cacheComScore[3][x][y] = score
        elif value == 2:
            cacheHumScore[3][x][y] = score
        result += score

    if value == 1: # 如果是电脑
        result = cacheComScore[0][x][y] + cacheComScore[1][x][y] +cacheComScore[2][x][y]  +cacheComScore[3][x][y] 
    elif value == 2:
        result = cacheHumScore[0][x][y] + cacheHumScore[1][x][y] +cacheHumScore[2][x][y]  +cacheHumScore[3][x][y] 

    return result

# 定义策略
ONE = 10
TWO = 100
THREE = 1000
FOUR = 100000
FIVE = 10000000
BLOCKED_ONE = 1
BLOCKED_TWO =  10
BLOCKED_THREE = 100
BLOCKED_FOUR = 10000
def countToScore(count, block, empty):
    #没有空位
    if empty <= 0:
        if count >= 5:
            return FIVE

        if block == 0:
            if count == 1:
                return ONE
            elif count == 2:
                return TWO
            elif count == 3:
                return THREE
            elif count == 4:
                return FOUR

        if block == 1:
            if count == 1:
                return BLOCKED_ONE
            elif count == 2:
                return BLOCKED_TWO
            elif count == 3:
                return BLOCKED_THREE
            elif count == 4:
                return BLOCKED_FOUR

    elif empty == 1 or empty == count-1: #这里是 or
        #第1个是空位
        if count >= 6:
            return FIVE
        
        if block == 0:
            if count == 2:
                return TWO/2
            elif count == 3:
                return THREE
            elif count == 4:
                return BLOCKED_FOUR
            elif count == 5:
                return FOUR

        if block == 1:
            if count == 2:
                return BLOCKED_TWO
            elif count == 3:
                return BLOCKED_THREE
            elif count == 4:
                return BLOCKED_FOUR
            elif count == 5:
                return BLOCKED_FOUR

    elif empty == 2 or empty == count-2:
        #第二个是空位
        if count >= 7:
            return FIVE
        
        if block == 0:
            if count == 3:
                return THREE
            elif count == 4 or count == 5:
                return BLOCKED_FOUR
            elif count == 6:
                return FOUR

        if block == 1:
            if count == 3:
                return BLOCKED_THREE
            elif count == 4:
                return BLOCKED_FOUR
            elif count == 5:
                return BLOCKED_FOUR
            elif count == 6:
                return FOUR

        if block == 2 and (count == 4 or count == 5 or count == 6):
            return BLOCKED_FOUR

    elif empty == 3 or empty == count-3:
        if count >= 8:
            return FIVE
        
        if block == 0:
            if count == 4 or count == 5:
                return THREE
            elif count == 6:
                return BLOCKED_FOUR
            elif count == 7:
                return FOUR

        if block == 1:
            if count == 4 or count == 5 or count == 6:
                return BLOCKED_FOUR
            elif count == 7:
                return FOUR

        if block == 2:
            if count == 4 or count == 5 or count == 6 or count == 7:
                return BLOCKED_FOUR

    elif empty == 4 or empty == count-4:
        if count >= 9:
            return FIVE
        
        if block == 0:
            if count == 8 or count == 5 or count == 6 or count == 7:
                return FOUR

        if block == 1:
            if count == 4 or count == 5 or count == 6 or count == 7:
                return BLOCKED_FOUR
            elif count == 8:
                return FOUR

        if block == 2:
            if count == 8 or count == 5 or count == 6 or count == 7:
                return BLOCKED_FOUR
    elif empty == 5 or empty == count-5:
        return FIVE
    
    return 0

# 获取剩下的可能下的点
# 直接看每个点是否有邻居即可！！！
def getAllNextPoints1(x):
    neighbors = []
    nextNeighbors = []
    i = 0
    for tempList in initChessList:
        j = 0
        for point in tempList:
            if point.value == 0 and hasNeighbor(i, j, 1):
                neighbors.append(SimplePoint(i, j))
                # s= "points: i:" + str(i) + "j:" + str(j)
                # print(s)
            j += 1
        i += 1
    return neighbors + nextNeighbors

# 升级为启发式函数
def getAllNextPoints(role):
    fives = []
    comfours=[]
    humfours=[]
    comblockedfours = []
    humblockedfours = []
    comtwothrees=[]
    humtwothrees=[]
    comthrees = []
    humthrees = []
    comtwos = []
    humtwos = []
    neighbors = []

    i = 0
    for tempList in initChessList:
        j = 0
        for point in tempList:
            if point.value == 0 and hasNeighbor(i, j, 1):
                scoreHum = broadHumScore[i][j]
                scoreCom = broadComScore[i][j]
                # if i == 5 and j == 8 and role == 2:
                    # print("scoreHum:" + str(broadHumScore[i][j]))
                p = SimplePoint(i, j)
                if scoreCom >= FIVE: #先看电脑能不能连成5
                    fives.append(p)
                elif scoreHum >= FIVE: #再看玩家能不能连成5,别急着返回，因为遍历还没完成，说不定电脑自己能成五。
                    fives.append(p)
                elif scoreCom >= FOUR:
                    comfours.append(p)
                elif scoreHum >= FOUR:
                    humfours.append(p)
                elif scoreCom >= BLOCKED_FOUR:
                    comblockedfours.append(p)
                elif scoreHum >= BLOCKED_FOUR:
                    humblockedfours.append(p)
                elif scoreCom >= 2*THREE:
                #能成双三也行
                    comtwothrees.append(p)
                elif scoreHum >= 2*THREE:
                    humtwothrees.append(p)
                elif scoreCom >= THREE:
                    comthrees.append(p)
                elif scoreHum >= THREE:
                    humthrees.append(p)
                elif scoreCom >= TWO:
                    comtwos.insert(0, p)
                elif scoreHum >= TWO:
                    humtwos.insert(0, p)
                else:
                    neighbors.append(p)
            j += 1
        i += 1
    
    #如果成五，是必杀棋，直接返回
    if len(fives) > 0:
        return fives
    
    # 自己能活四，则直接活四，不考虑冲四
    if role == 1 and len(comfours) > 0:
        return comfours
    if role == 2 and len(humfours) > 0:
        return humfours

    # 对面有活四冲四，自己冲四都没，则只考虑对面活四 （此时对面冲四就不用考虑了)
    
    if role == 1 and len(humfours) > 0 and len(comblockedfours) <= 0:
        return humfours
    if role == 2 and len(comfours) > 0 and len(humblockedfours) <= 0:
        return comfours

    # 对面有活四自己有冲四，则都考虑下
    if role == 1:
        fours = comfours + humfours
        blockedfours = comblockedfours + humblockedfours
    else:
        fours = comfours + humfours
        blockedfours = humblockedfours + comblockedfours

    if len(fours) > 0:
        return fours + blockedfours

    result = []
    if role == 1:
      result = comtwothrees + humtwothrees + comblockedfours + humblockedfours + comthrees + humthrees
    
    if role == 2:
      result = humtwothrees + comtwothrees + humblockedfours + comblockedfours + humthrees + comthrees

    # result.sort(function(a, b) { return b.score - a.score })

    # 双三很特殊，因为能形成双三的不一定比一个活三强
    if len(comtwothrees) > 0 or len(humtwothrees) > 0: 
      return result
    


    # 只返回大于等于活三的棋
    # if (onlyThrees) {
    #   return result
    # }


    twos = []
    if role == 1:
        twos = comtwos + humtwos
    else :
        twos = humtwos + comtwos

    # twos.sort(function(a, b) { return b.score - a.score })
    if twos != None and len(twos) > 0:
        result += twos
    else :
        result += neighbors

    return result

def hasNeighbor(x, y, len):
    if x + len < 15 and initChessList[x + len][y].value != 0:
        return True
    if x - len >= 0 and initChessList[x - len][y].value != 0:
        return True
    if y + len < 15 and initChessList[x][y + len].value != 0:
        return True
    if y - len >= 0 and initChessList[x][y - len].value != 0:
        return True
    if x + len < 15 and y + len < 15 and initChessList[x + len][y + len].value != 0:       
        return True
    if x - len >= 0 and y - len >= 0 and initChessList[x - len][y - len].value != 0:
        return True
    if y + len < 15 and x - len >= 0 and initChessList[x - len][y + len].value != 0:
        return True
    if y - len >= 0 and x + len < 15 and initChessList[x + len][y - len].value != 0:
        return True
    # s = "X" + str(x) + " Y" + str(y) + ":false"
    # print(s)
    # 看看期盼状态
    return False

def updateBroadScore(): # 先全部更新，后面再针对性更新
    i = 0
    for temp in initChessList:
        j = 0
        for point in temp:
            if i > 14 or j > 14:
                break

            if point.value == 1:
                broadComScore[i][j] = getScoreWithPoint(i, j, 1, -1)
                # s = "com x -> "+ str(j) + " y ->"+ str(i) + " Result : " + str(broadComScore[i][j])
                # s1= " point x " + str(point.x) + " point y " + str(point.y)
                # print(s + s1)
            elif point.value == 2:
                broadHumScore[i][j] = getScoreWithPoint(i, j, 2, -1)
            # print(point.value, end=" ")
            elif point.value == 0:
                # print("i" + str(i) + " j" + str(j)) 
                broadHumScore[i][j] = 0
                broadComScore[i][j] = 0
            j += 1
        # print("\t")
        i += 1
    # print("\t")

# 更新某个点
def updatePointScore(x, y): # 先全部更新，后面再针对性更新
    # print("update!")
    for i in range(0, 9): # 这里没有负数
        tx = x
        ty = y + i - 4
        # if x == 6 and y == 8:
        #     print("updatePointScore 8 6:" + str(ty) + " " + str(tx))
        if ty < 0 or ty > 14:
            continue
        update(tx, ty, 0)  # 靠，忘记改update了
    
    for i in range(0, 9):
        tx = x + i - 4
        ty = y
        # if x == 6 and y == 8:
        #     print("updatePointScore 8 6:" + str(ty) + " " + str(tx))
        if tx < 0 or tx > 14:
            continue
        # if tx == 5 and ty == 8:
        #     print("updatePointScore 8 5 update:")
        update(tx, ty, 1)

    for i in range(0, 9):
        tx = x + i - 4
        ty = y + i - 4
        # if tx == 6 and ty == 10:
        #     print("updatePointScore 10 6:" + str(ty) + " " + str(tx))
        if ty < 0 or ty > 14 or tx < 0 or tx > 14:
            continue
        update(tx, ty, 2)

    for i in range(0, 9):
        tx = x + i - 4
        # ty = y - i - 4
        ty = y - i + 4
        # if x == 7 and y == 9:
        #     print("tx:" + str(tx) + " ty:" + str(ty))
        # if tx == 6 and ty == 10:
        #     print("updatePointScore 10 6:" + str(ty) + " " + str(tx))
        if ty < 0 or ty > 14 or tx < 0 or tx > 14:
            continue
        update(tx, ty, 3)



def update(x, y, dir): # 用于更新点里面的函数，指定方向更新
    if x == 6 and y == 10:
        print("10 6 --->" + str(initChessList[x][y].value))
    if initChessList[x][y].value == 0:
        broadHumScore[x][y] = getScoreWithPoint(x, y, 2, dir)
        if x == 6 and y == 10 and dir == 0:
            print("scoreHum: " + str(cacheHumScore[0][x][y]) + " " + str(cacheHumScore[1][x][y]) + " " + str(cacheHumScore[2][x][y]) + " " + str(cacheHumScore[3][x][y]))
        broadComScore[x][y] = getScoreWithPoint(x, y, 1, dir)
    elif initChessList[x][y].value == 1:
        broadHumScore[x][y] = 0
        broadComScore[x][y] = getScoreWithPoint(x, y, 1, dir)
    elif initChessList[x][y].value == 2: # 这里失误了，忘记加0
        broadHumScore[x][y] = getScoreWithPoint(x, y, 2, dir)
        broadComScore[x][y] = 0

# 初始化是不是搞错了，导致后面的一些位置没有分数
def initScore():
    i = 0
    for temp in initChessList:
        j = 0
        for point in temp:
            if i > 14 or j > 14:
                break
            if point.value == 1:
                broadHumScore[i][j] = 0
                broadComScore[i][j] = getScoreWithPoint(i, j, 1, -1)
            elif point.value == 2:
                broadHumScore[i][j] = getScoreWithPoint(i, j, 2, -1)
                broadComScore[i][j] = 0
            elif point.value == 0 and hasNeighbor(i, j, 1):
                broadHumScore[i][j] = getScoreWithPoint(i, j, 2, -1)
                broadComScore[i][j] = getScoreWithPoint(i, j, 1, -1)
            j += 1
        # print("\t")
        i += 1

def evalute(value):
    result = 0
    for i in range(15):
        for j in range(15):
            if initChessList[i][j].value == 1:
                result += broadComScore[i][j]
            elif initChessList[i][j].value == 2:
                result -= broadHumScore[i][j]
    # if value == 2:
    #     return -result
    return result

# 下子并更新分数
def put(x, y, value):
    # print("下子--->" + str(y) + " " + str(x) + " " + str(value))
    initChessList[x][y].value = value
    updatePointScore(x, y)

# 撤回并更新分数
def remove(x, y):
    # print("撤回--->" + str(y) + " " + str(x) + " ")
    initChessList[x][y].value = 0
    updatePointScore(x, y)

MAX = 100000000
MIN = -100000000
# 极大极小数
def funcMaxMin(deep):
    # 拿到
    global ABcut  #统计剪枝次数
    ABcut = 0
    best = MIN
    points = []
    points = getAllNextPoints(1)
    s = "第一次拿到的points" + str(len(points))
    print(s)
    for p in points:
        s =" " + str( p.y ) + " " + str( p.x )
        print(s)
    resultPoints = []
    alpha = MAX
    beta = MIN


    for p in points:

        if best > beta:
            beta = best   # 这里的逻辑有问题：tempBeta = best

        # initChessList[p.x][p.y].value = 1
        s = "极大极小第一层 横坐标 - >" + str(p.y) + "纵坐标 - >" + str(p.x) + "  begin!"
        print(s)
        put(p.x, p.y, 1)
        v = funcMin(deep - 1, p, MAX, beta)
        
        # initChessList[p.x][p.y].value = 0
        remove(p.x, p.y)
        s = "极大极小第一层 横坐标 - >" + str(p.y) + "纵坐标 - >" + str(p.x) + "v - > " + str(v) + "结束"
        print(s)
        if best < v:
            best = v
            resultPoints = []
            resultPoints.append(p)
            # if v >= 10000000: 不能直接放在这，>10000000不一定是最优解
            #     break
        if best == v:
            resultPoints.append(p)
    
    print("剪枝----->" + str(ABcut))
    return random.choice(resultPoints)  


def funcMax(deep, p, alpha, beta):
    # s = "极大层 deep - >" + str(deep)
    # print(s)
    global ABcut

    if deep < 0 or judgeResult(p.x, p.y, 2):
        # updateBroadScore()
        r = evalute(2)
        return r
    
    best = MIN
    points = []
    points = getAllNextPoints(1)
    for p in points:
        # initChessList[p.x][p.y].value = 1
        put(p.x, p.y, 1)

        if best > beta:         # 这里的逻辑需要修改吗
            beta = best

        v = funcMin(deep - 1, p, alpha, beta)
        # initChessList[p.x][p.y].value = 0
        remove(p.x, p.y)
        if best < v:
            best = v
        if v > alpha:
            ABcut += 1
            break
    return best

def funcMin(deep, p, alpha, beta):
    # s = "极小层 deep - >" + str(deep)
    # print(s)
    global ABcut

    if deep < 0 or judgeResult(p.x, p.y, 1):
        # updateBroadScore()
        r = evalute(1)
        return r
    
    best = MAX
    points = []
    points = getAllNextPoints(2)
    for p in points:
        # initChessList[p.x][p.y].value = 2
        put(p.x, p.y, 2)

        if best < alpha:
            alpha = best

        v = funcMax(deep - 1, p, alpha, beta) # 获取极小值
        # initChessList[p.x][p.y].value = 0
        remove(p.x, p.y)
        if best > v:
            best = v
        if v < beta: # 剪枝:极小层估值小于beta
            ABcut += 1
            break

    return best

def eventHander():            #监听各种事件
    for event in pygame.event.get():
        global initRole,resultFlag,lastP
        if event.type == QUIT:#事件类型为退出时
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN: #当点击鼠标时
            x,y = pygame.mouse.get_pos()  #获取点击鼠标的位置坐标
            i=0
            j=0
            for temp in initChessList:
                for point in temp:
                    if x>=point.x-10 and x<=point.x+10 and y>=point.y-10 and y<=point.y+10:
                        if point.value == 0 and initRole == 1:   #当棋盘位置为空；棋子类型为白棋
                            point.value = 1             #鼠标点击时，棋子为白棋
                            if judgeResult(i,j,1):               #如果条件成立，证明五子连珠
                                resultFlag = 1 #获取成立的棋子颜色
                                print("白棋赢")
                            # s = "white score result --> " + str(getScoreWithPoint(i, j, 1))
                            s1 = "横坐标 -> " + str(j) + " 纵坐标 - >" + str(i)
                            print(s1)
                            initRole = 2                #切换角色
                        elif point.value == 0 and initRole ==2:  #当棋盘位置为空；棋子类型为黑棋
                            # point.value = 2             #鼠标点击时，棋子为黑棋
                            put(i, j, 2)
                            if judgeResult(i,j,2):               #如果条件成立，证明五子连珠
                                resultFlag = 2 #获取成立的棋子颜色
                                print("黑棋赢")
                                break           
                            # s = "black score result --> " + str(getScoreWithPoint(i, j, 2))
                            # print(s)
                            
                            screen.blit(blackStorn,(point.x-18,point.y-18))
                            pygame.display.update()                #更新视图    

                            initRole = 1                #切换角色
                            # updateBroadScore()
                            p = funcMaxMin(3)
                            s = "下一步棋可以是: 横坐标 -> " + str(p.y) + " 纵坐标 - >" + str(p.x)
                            print(s)
                            # initChessList[p.x][p.y].value = 1
                            put(p.x, p.y, 1)
                            lastP.x = initChessList[p.x][p.y].x          #记录之前的p
                            lastP.y = initChessList[p.x][p.y].y 
                            if judgeResult(p.x,p.y,1):               #如果条件成立，证明五子连珠
                                resultFlag = 1 #获取成立的棋子颜色
                                print("白棋赢")
                                break
                            initRole = 2

                        break
                    j+=1
                i+=1 #纵坐标
                j=0  #横坐标

# 加载素材
def main():
    global initChessList,resultFlag,screen,blackStorn, whiteStorn,initRole,lastP
    initChessSquare(27,27)
    pygame.init()     # 初始化游戏环境
    screen = pygame.display.set_mode((620,620),0,0)          # 创建游戏窗口 # 第一个参数是元组：窗口的长和宽
    pygame.display.set_caption("五子棋")                # 添加游戏标题
    background = pygame.image.load("images/bgx.png")          #加载背景图片
    whiteStorn = pygame.image.load("images/storn_white.png") #加载白棋图片
    blackStorn = pygame.image.load("images/storn_black.png") #加载黑棋图片
    resultStorn = pygame.image.load("images/resultStorn.jpg")#加载 赢 时的图片
    resultShu = pygame.image.load("images/shu100.jpg")#加载 输 时的图片
    lastStorn = pygame.image.load("images/焦点30.png")#加载 上次 的图片

    rect = blackStorn.get_rect()
    initChessList[7][7].value = 1
    put(7, 7, 1)
    # initScore()  # 初始化分数
    while True:
        screen.blit(background,(0,0))
        for temp in initChessList:
            for point in temp:
                if point.value == 1:          #当棋子类型为1时，绘制白棋
                    screen.blit(whiteStorn,(point.x-18,point.y-18))
                elif point.value == 2:        #当棋子类型为2时，绘制黑棋
                    screen.blit(blackStorn,(point.x-18,point.y-18))
                if lastP.x == point.x and lastP.y == point.y:
                    screen.blit(lastStorn,(point.x-15,point.y-15))

        if resultFlag >0:
            initChessList = []                 # 清空棋盘
            initChessSquare(27,27)             # 重新初始化棋盘
            if resultFlag == 1:
                screen.blit(resultShu,(20,20)) #绘制获胜时的图片
            else :
                screen.blit(resultStorn,(20,20)) #绘制获胜时的图片
        pygame.display.update()                #更新视图

        if resultFlag >0:
            time.sleep(5)
            resultFlag = 0                     #置空之前的获胜结果
            initChessList[7][7].value = 1
            initScore()
            initRole = 2
        eventHander()                          #调用之前定义的事件函数


if __name__ == '__main__':
    main()        #调用主函数绘制窗口
    pass



