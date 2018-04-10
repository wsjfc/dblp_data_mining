import pandas as pd
import pyfpgrowth
import re
import pickle

class DblpData:
    def __init__(self,f):
        f = open(f, 'r')
        self.data = self.__getdata(f)

    def __getData(self,f):
        '''

        :param f:包含原始会议数据的文件
        :return: dataframe格式存储的数据
        '''
        count = 1
        author, title, year, confe, at, authorStr = list(), list(), list(), list(), list(), list()
        at = []

        while True:
            content = f.readline()
            if content:
                content = content.strip('\n').split('\t')
                if content[0] == 'author':
                    at.append((content[1]))
                if content[0] == 'title':
                    tt = content[1]
                if content[0] == 'year':
                    yr = content[1]
                if content[0] == 'Conference':
                    ce = content[1]
                elif content[0] == '#########':
                    if count != 1:
                        at = sorted(at)
                        atStr = ','.join(at)
                        author.append(at)
                        authorStr.append(atStr)
                        title.append(tt)
                        year.append(yr)
                        confe.append(ce)
                        at = []
                    count += 1
            else:
                at = sorted(at)
                atStr = ','.join(at)
                author.append(at)
                title.append(tt)
                year.append(yr)
                confe.append(ce)
                authorStr.append(atStr)
                break

        datadict = {'author': author, 'title': title, 'year': year, 'confe': confe,'authorStr':authorStr}
        df = pd.DataFrame(datadict)

        return df

#将fp-find后返回的字典转换为dataframe形式存储并去掉重复条目
def filter_data(fpData1, fpData2):
    dataDict1 = fpData1
    dataDict2 = fpData2
    authorArticleNum = dict()

    for authorName in dataDict2.keys():
        authorList = [name for name in authorName]
        authorArticleNum[','.join(sorted(authorList))] = dataDict2[authorName]

    name, num, names, authorNamesSet = list(), list(), list(), list()

    for authorName1, authorName2 in dataDict1.items():
        authorNames = []
        if len(authorName2) > 1:
            for i in authorName1:
                authorNames.append(i)
            for j in authorName2[0]:
                authorNames.append(j)
        authorNames = sorted(authorNames)

        if authorNames not in authorNamesSet and len(authorNames) > 2:
            authorNamesSet.append(authorNames)
            name = ','.join(authorNames)
            names.append(name)
            num.append(authorArticleNum[name])

    dic = {'author_names':names,'article_nums':num}
    df = pd.DataFrame(dic,columns=['author_names','article_nums'])

    return df

#频繁模式挖掘
def fp_minimg(author,support = 5,confidence = 0.8):
    patterns = pyfpgrowth.find_frequent_patterns(author, support)
    rules = pyfpgrowth.generate_association_rules(patterns, confidence)
    return patterns,rules

#找到各个会议的支持者
def find_supporter(datas,confenames,years,threshold = 5):
    authorinfos = dict()
    differconfe = dict()
    yearlist = [0]*11
    for confename in confenames:
        for year in years:
            data_s = datas[datas['year'] == year]
            authordf =data_s[data_s['confe'] == confename]
            for i in range(len(authordf['author'].values)):
                for j in authordf['author'].values[i]:
                    if not(j in authorinfos.keys()):
                        yearlist[int(year)-2007] += 1
                        authorinfos[j] = yearlist
                    else:
                        authorinfos[j][int(year)-2007] += 1
                    yearlist = [0]*11
        supporterdf = pd.DataFrame(authorinfos).T
        modify_sup = supporterdf[supporterdf.sum(axis = 1) >= threshold]
        differconfe[confename] = modify_sup
        authorinfos = {}

    return differconfe

#找到依旧活跃的支持者
def find_still_active_sup(difconsup,threshold = 0.3):
    active_sup = dict()
    for confename in difconsup.keys():
        df = difconsup[confename]
        activesup = df[df[[8,9,10]].sum(axis = 1) > threshold*df.sum(axis = 1)]
        active_sup[confename] = activesup

    return active_sup

def get_author_info():#获取作者信息，用一个字符串文本存储
    f = open('FilteredDBLP.txt','r')
    authorNames = ''
    authorName = list()

    while True:
        content = f.readline()

        if content:
            content = content.strip('\n').split('\t')
            if content[0] == 'author':
                authorName.append(content[1])

            elif content[0] == '#########':
                authorName = ','.join(sorted(authorName))
                authorNames = authorNames + authorName + '\n'
                authorName = []
        else:
            break

    return authorNames

def get_title_group_info():#获取团体合作发表的文章信息，以字典形式存储
    nameText = get_author_info()
    data = DblpData('FilteredDBLP.txt')
    authorDf = pd.read_csv('/home/jfc/PycharmProjects/dblp/output/output.csv')
    titleList = list()
    authorArticleDict = dict()
    articleYearDict = dict()
    name2numDict = name2num(authorDf)
    a,b,c,d = list(),list(),list(),list()
    yearGroupDict = {'a':a, 'b':b, 'c':c, 'd':d}

    for i in authorDf['author_names'].values:
        names = sorted(i.split(','))
        comparison = '.*' + '.*'.join(names) + '.*'

        for j in {}.fromkeys(re.findall(comparison, nameText)).keys():

            for title in data.data[data.data['author_str'] == j]['title'].values:
                year = data.data[data.data['title'] == title]['year'].values[0]
                articleYearDict[title.strip('.')] = year
                titleList.append(articleYearDict)
                if not ','.join(sorted(i.split(','))) in yearGroupDict[yearCut(year)]:
                    yearGroupDict[yearCut(year)].append(','.join(sorted(i.split(','))))

        authorArticleDict[i] = titleList
        articleYearDict = {}
        titleList = []

    return authorArticleDict, yearGroupDict

def name2num(authorNameDf):
    name2numDict = dict()
    num = 0
    for name in authorNameDf['author_names'].values:
        name2numDict[name] = num
        num += 1

    return name2numDict

def yearCut(year):#将年份按3年为间隔划分为区间
    year = int(year)
    if year >= 2007 and year < 2010:
        return 'a'
    if year >= 2010 and year <2013:
        return 'b'
    if year >= 2013 and year <2016:
        return 'c'
    if year >= 2016 and year <2019:
        return 'd'
if __name__ == '__main__':

    data = DblpData('FilteredDBLP.txt')
    patterns,rules = fp_minimg(data.data['author'].values)
    coAuthor = filter_data(rules, patterns)
    coAuthor.to_csv('/home/jfc/PycharmProjects/dblp/output/output.csv')

    years = tuple(map(str,range(2007,2018)))
    confeNames = ['IJCAI', 'AAAI', 'COLT', 'CVPR', 'NIPS', 'KR', 'SIGIR', 'KDD']
    threshold = 7
    differConfeSup = find_supporter(data.data, confeNames, years, threshold)
    PATH = '/home/jfc/PycharmProjects/dblp/output2/'
    for i in confeNames:
        f = PATH + i + '.csv'
        differConfeSup[i].to_csv(f)

    threshold = 0.2
    stillActiveSup = find_still_active_sup(differConfeSup, threshold)
    PATH = '/home/jfc/PycharmProjects/dblp/output/'
    for i in confeNames:
        f = PATH + i + '.csv'
        stillActiveSup[i].to_csv(f)

    authotArticleDict, yearGroupDict = get_title_group_info()
    with open('/dev/shm/pytmp1.txt', 'wb') as f:  # 中间结果保存在内存中
        pickle.dump(authotArticleDict, f)
    f.close()
    with open('/dev/shm/pytmp2.txt', 'wb') as f:
        pickle.dump(yearGroupDict, f)
    f.close()















