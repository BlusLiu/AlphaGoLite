import pygame        #导入pygame游戏模块
import time
import sys
import random
from pygame.locals import *

initChessList = []          #保存的是棋盘坐标
initRole = 2                #1：代表白棋； 2：代表黑棋
resultFlag = 0              #结果标志

broadHumScore = []
broadComScore = []

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
        scoreHum = []
        scoreCom = []
        for j in range(15):   # 每一列的交叉点坐标
            pointX = x+ j*40
            pointY = y+ i*40
            sp = StornPoint(pointX,pointY,0)
            rowlist.append(sp)
            scoreHum.append(0)
            scoreCom.append(0) 
        initChessList.append(rowlist)
        broadHumScore.append(scoreHum)
        broadComScore.append(scoreCom)

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
                            s = "white score result --> " + str(getScoreWithPoint(i, j, 1))
                            s1 = "横坐标 -> " + str(j) + " 纵坐标 - >" + str(i)
                            print(s + s1)
                            initRole = 2                #切换角色
                        elif point.value == 0 and initRole ==2:  #当棋盘位置为空；棋子类型为黑棋
                            point.value = 2             #鼠标点击时，棋子为黑棋
                            if judgeResult(i,j,2):               #如果条件成立，证明五子连珠
                                resultFlag = 2 #获取成立的棋子颜色
                                print("黑棋赢")
                                break
                            s = "black score result --> " + str(getScoreWithPoint(i, j, 2))
                            print(s)
                            initRole = 1                #切换角色
                            screen.blit(blackStorn,(point.x-18,point.y-18))
                            if lastP.x != -1 and lastP.y != -1:
                                 screen.blit(whiteStorn,(lastP.x-19,lastP.y-19))
                            lastP.x = -1
                            lastP.y = -1
                            pygame.display.update()                #更新视图    

                            updateBroadScore()
                            p = funcMaxMin(3)
                            s = "下一步棋可以是: 横坐标 -> " + str(p.y) + " 纵坐标 - >" + str(p.x)
                            print(s)
                            initChessList[p.x][p.y].value = 1
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

def getScoreWithPoint(x,y,value):   #横向判断
    count1 = 1
    count2 = 0
    enemyNum = 0
    empty = -1
    result = 0
    # s = "count1 " + str(count1) + " count2 " + str(count2) + " x " + str(x) + " enemyNum " + str(enemyNum) + " empty " + str(empty) + " result " + str(result)
    # print(s)

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
    result += countToScore(count1 + count2, enemyNum, empty)

    count1 = 1
    count2 = 0
    enemyNum = 0
    empty = -1

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
    result += countToScore(count1 + count2, enemyNum, empty)

    count1 = 1
    count2 = 0
    enemyNum = 0
    empty = -1

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
    result += countToScore(count1 + count2, enemyNum, empty)

    count1 = 1
    count2 = 0
    enemyNum = 0
    empty = -1

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
    result += countToScore(count1 + count2, enemyNum, empty)

    # if value == 1: # 如果是电脑
    #     broadComScore[x][y] = result
    # elif value == 2:
    #     broadHumScore[x][y] = result

    return result

def countToScore(count, block, empty):
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
def getAllNextPoints(deep):
    neighbors = []
    nextNeighbors = []
    i = 0
    for tempList in initChessList:
        j = 0
        for point in tempList:
            if point.value == 0:
                if hasNeighbor(i, j, 1):
                    neighbors.append(SimplePoint(i, j))
                    # s= "points: i:" + str(i) + "j:" + str(j)
                    # print(s)
                elif deep < -1 and hasNeighbor(i, j, 2): # 这里加个deep的判断
                    nextNeighbors.append(SimplePoint(i, j))
            j += 1
        i += 1
    return neighbors + nextNeighbors

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
                broadComScore[i][j] = getScoreWithPoint(i, j, 1)
                # s = "com x -> "+ str(j) + " y ->"+ str(i) + " Result : " + str(broadComScore[i][j])
                # s1= " point x " + str(point.x) + " point y " + str(point.y)
                # print(s + s1)
            elif point.value == 2:
                broadHumScore[i][j] = getScoreWithPoint(i, j, 2)
            # print(point.value, end=" ")
            elif point.value == 0:
                # print("i" + str(i) + " j" + str(j)) 
                broadHumScore[i][j] = 0
                broadComScore[i][j] = 0
            j += 1
        # print("\t")
        i += 1
    # print("\t")

def evalute(value):
    result = 0
    for i in range(15):
        for j in range(15):
            result += (broadComScore[i][j] - broadHumScore[i][j])
    # if value == 2:
    #     return -result
    return result

MAX = 100000000
MIN = -100000000
# 极大极小数
def funcMaxMin(deep):
    # 拿到
    global ABcut  #统计剪枝次数
    ABcut = 0
    best = MIN
    points = []
    points = getAllNextPoints(deep)
    s = "第一次拿到的points" + str(len(points))
    print(s)
    resultPoints = []
    alpha = MAX
    beta = MIN


    for p in points:

        if best > beta:
            tempBeta = best
        else :
            tempBeta = beta

        initChessList[p.x][p.y].value = 1
        v = funcMin(deep - 1, p, MAX, tempBeta)
        s = "极大极小第一层 横坐标 - >" + str(p.y) + "纵坐标 - >" + str(p.x) + "v - > " + str(v)
        print(s)
        initChessList[p.x][p.y].value = 0
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
        updateBroadScore()
        r = evalute(2)
        return r
    
    best = MIN
    points = []
    points = getAllNextPoints(deep)
    for p in points:
        initChessList[p.x][p.y].value = 1

        if best > beta:
            tempBeta = best
        else :
            tempBeta = beta

        v = funcMin(deep - 1, p, alpha, tempBeta)
        initChessList[p.x][p.y].value = 0
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
        updateBroadScore()
        r = evalute(1)
        return r
    
    best = MAX
    points = []
    points = getAllNextPoints(deep)
    for p in points:
        initChessList[p.x][p.y].value = 2

        if best < alpha:
            tempAlpha = best
        else :
            tempAlpha = alpha

        v = funcMax(deep - 1, p, tempAlpha, beta) # 获取极小值
        initChessList[p.x][p.y].value = 0
        if best > v:
            best = v
        if v < beta: # 剪枝
            ABcut += 1
            break

    return best


# 加载素材
def main():
    global initChessList,resultFlag,screen,blackStorn, whiteStorn,initRole,lastP
    initChessSquare(27,27)
    pygame.init()     # 初始化游戏环境
    screen = pygame.display.set_mode((620,620),0,0)          # 创建游戏窗口 # 第一个参数是元组：窗口的长和宽
    pygame.display.set_caption("五子棋")                # 添加游戏标题
    background = pygame.image.load("images/bg.png")          #加载背景图片
    whiteStorn = pygame.image.load("images/storn_white.png") #加载白棋图片
    blackStorn = pygame.image.load("images/storn_black.png") #加载黑棋图片
    resultStorn = pygame.image.load("images/resultStorn.jpg")#加载 赢 时的图片
    resultShu = pygame.image.load("images/shu100.jpg")#加载 输 时的图片
    lastStorn = pygame.image.load("images/焦点36.png")#加载 上次 的图片

    rect = blackStorn.get_rect()
    initChessList[7][7].value = 1
    while True:
        screen.blit(background,(0,0))
        for temp in initChessList:
            for point in temp:
                if point.value == 1:          #当棋子类型为1时，绘制白棋
                    screen.blit(whiteStorn,(point.x-18,point.y-18))
                elif point.value == 2:        #当棋子类型为2时，绘制黑棋
                    screen.blit(blackStorn,(point.x-18,point.y-18))
                if lastP.x == point.x and lastP.y == point.y:
                    screen.blit(lastStorn,(point.x-18,point.y-18))

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
            initRole = 2
        eventHander()                          #调用之前定义的事件函数
if __name__ == '__main__':
    main()        #调用主函数绘制窗口
    pass



