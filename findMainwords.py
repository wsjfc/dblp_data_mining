import pickle
import pandas as pd
from gensim import corpora,models
from collections import Counter
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import posTag,wordTokenize
from findSupport import yearCut

class MainTopic:
    '''
    实现两个功能，即以tfidf加权后的词频以及原始词频排名作为主题词选取依据挖掘出的主题词
    '''
    def __init__(self):
        with open('/dev/shm/pytmp3.txt','rb') as f:
            self.all_articles = pickle.load(f)
            f.close()

    def tfidf_topic(self, articles, threshold = 2):
        '''
        :param 文章标题:
        :param threshold:
        :return: tfidf加频后挖掘出的主题词
        '''
        dictionary = corpora.Dictionary(self.all_articles)
        corpus = [dictionary.doc2bow(article) for article in self.all_articles]
        tfidf = models.TfidfModel(corpus)
        articles = dictionary.doc2bow(articles)
        corpusTfidf = tfidf[articles]
        c = tuple2dict(corpusTfidf)
        if len(c.values()) > threshold:
            commonWord = [dictionary[key] for key, value in c.items() if
                          value >= sorted(c.values(), reverse=True)[threshold]]
        else:
            commonWord = [dictionary[key] for key in c.keys()]

        return commonWord

    def frequence_topic(self,articles,threshold = 1):
        '''

        :param 文章标题:
        :param threshold:
        :return: 原始词频为依据挖掘出的主题词
        '''

        c = Counter(articles)
        if len(c.values()) > threshold:
            commonWord = [key for key, value in c.items() if
                          value >= sorted(c.values(), reverse=True)[threshold]]
        else:
            commonWord = [key for key in c.keys()]

        return commonWord

def get_wordnet_pos(treebankTag):
    '''

    :param posTag:
    :return: 可以直接被lemmatize利用的pos_tag
    '''

    if treebankTag.startswith('J'):
        return wordnet.ADJ
    elif treebankTag.startswith('V'):
        return wordnet.VERB
    elif treebankTag.startswith('N'):
        return wordnet.NOUN
    elif treebankTag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def tuple2dict(tup):
    dictionary =dict()
    for i in tup:
        dictionary[i[0]] = i[1]

    return dictionary

def get_all_articles(authortTitle):
    '''

    :param :每一个团队及其发表的文章的标题
    :return:所有标题揉杂在一起的语料库
    '''
    allArticles = list()
    wordnetLemmatizer = WordNetLemmatizer()

    for titles in authortTitle.values():
        titles = list(titles[0].keys())
        pos_tokens = [posTag(wordTokenize(title.lower())) for title in titles]
        words = [[(wordnetLemmatizer.lemmatize(word, pos=get_wordnet_pos(postag))) for (word, postag) in pos if
                  postag.startswith('V') or postag.startswith('N')] for pos in pos_tokens]
        groupArticle = []
        for text in words:
            for word in text:
                groupArticle.append(word)
        allArticles.append(groupArticle)

    with open('/dev/shm/pytmp3.txt', 'wb') as f:
        pickle.dump(allArticles, f)
        f.close()

def get_topic_list(groupArticle, threshold1 = 2, threshold2 = 1):
    topics = MainTopic()
    tfidfWords = topics.tfidf_topic(groupArticle, threshold1)
    frequenceWords = topics.frequence_topic(groupArticle, threshold2)
    tfidfWordStr = ','.join(tfidfWords)
    frequenceWordStr = ','.join(frequenceWords)
    topicList = [tfidfWordStr, frequenceWordStr]

    return topicList

def get_mainword(nameTitles):
    wordnetLemmatizer = WordNetLemmatizer()
    topicDict1, topicDict2, topicDict3 = dict(), dict(), dict()

    for author, articleYear in nameTitles.items():
        titles = list(articleYear[0].keys())
        years = list(articleYear[0].values())
        posTokens = [posTag(wordTokenize(title.lower())) for title in titles]
        words = [[(wordnetLemmatizer.lemmatize(word, pos = get_wordnet_pos(postag))) for (word, postag) in pos if
                  postag.startswith('V') or postag.startswith('N')] for pos in posTokens]
        groupArticle = []
        tfidfYearArticle = {}
        frequentYearArticle = {}
        yearArticle = {}

        for text,year in zip(words,years):
            if yearCut(year) not in yearArticle.keys():
                yearArticle[yearCut(year)] = ','.join(text)
            else:
                yearArticle[yearCut(year)] = yearArticle[yearCut(year)] + ','.join(text)

            for word in text:
                groupArticle.append(word)
        for key,value in yearArticle.items():
            topic = get_topic_list(value.split(','), 3, 3)
            tfidfYearArticle[yearCut(year)] =  topic[0]
            frequentYearArticle[yearCut(year)] = topic[1]
        topicDict1[author] = get_topic_list(groupArticle, 3, 3)
        topicDict2[author] = tfidfYearArticle
        topicDict3[author] = frequentYearArticle

    pd.DataFrame(topicDict1).T.to_csv('theme.csv')
    pd.DataFrame(topicDict2).T.to_csv('theme2.csv')
    pd.DataFrame(topicDict3).T.to_csv('theme3.csv')

if __name__ == '__main__':
    with open('/dev/shm/pytmp1.txt', 'rb') as f:
        authorTitleDict = pickle.load(f)
    f.close()

    get_all_articles(authorTitleDict)
    get_mainword(authorTitleDict)
