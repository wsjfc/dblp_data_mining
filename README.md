# 任务说明
## 任务一
每一个会议都有各自的支持者,将每个会议各自的研究者寻找出来,并且根据时间信息,看看哪些人依然活跃,哪些人不再活跃。
* 先从原始文件中导入作者、文章标题、发表年份等信息。
* 按会议统计各个会议中不同作者发表的文章数,设置一定的历史发表文章数作为阈
值,历史发表文章数大于阈值的作者作为该会议支持者。
* 按每位作者随时间变化的文章发表情况来筛选哪些作者依然活跃,哪些作者不再活
跃;具体而言,统计一位作者在一个会议上发表文章数量在所有作者发表文章数量的排名,
排名高于一定排名阈值则说明其在该年度比较活跃,低于一定排名阈值则说明其活跃度降低
或者不活跃。
## 任务二
在找到各自的研究者群体后,希望找到经常性在一起合作的学者,将之称为“团队”。
* 在所有会议的历年投稿数据中,用FP-growth算法对每一篇文章的作者进行频繁模式挖掘,按设定的阈值筛选出所有满足的团队;
* 由于可能出现集合和其子集都满足条件,从而在统计时重复的情况,这时我们将其进行筛选使这些集合统一于一个集合。
## 任务三
每一篇论文都会涉及到一个或多个主题,先定出主题词, 然后根据每个“团队”发表的论文的情况,提炼出这个团队最常涉猎的主题。
* 在基于前一题寻找团队的分析成果上,先将文章按作者团队分配给每个团队;
* 接着将属于一个团队的所有文章标题组合到一个容器中(即将一个团队的所有文章
标题当做一篇文档看,此时所有的文章标题组成的集合就是语料库);
* 最后分别利用词频统计以及 tfidf 的方法来得到每个集合中词频高或者 tfidf 得分高
的词,设置合理的阈值筛选出这个团队有代表性的研究主题。
## 任务四
团队和主题多是会随着时间而动态变化。根据所定的时间段(三年)描述团队的构成状况以及其研究主题的变化情况。
* 选择一个时间段(3年)作为描述团队成员构成状况以及其研究主题的变化情况的基准,将07到17年按照3年为间隔划分,共分为4个区间(07~09,10~12,13~15,16~17);
* 按这个时间段划分数据集并结合之前写的函数得到每三年的主要团队集合;
* 按照“前后两个时间段的团队集合中,若有一个前一时间段团队组成和后一时间段的团队组成的重合度大于0.5,我们认为这个团队仍然存在,只是发生了人员的变动(partions changed);若小于0.5我们就认为这个前一阶段存在的团队在后一个阶段不再存在了;若等于1则这个团队完整保留下来了(not change)”的原则将相临两个时间段的团队集合进行分析,得到团队构成的变动情况;
* 将每个时间段的较前一时间段“完整保留”和“小范围人员变动”的团队视为一个整体运行提炼团队主体的函数得到团队的研究主题变化情况。
