import numpy as np
import pandas as pd
from scipy.stats import kstest
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from apyori import apriori
import datetime as dt
from sklearn.decomposition import PCA
from sklearn import svm
from sklearn import preprocessing
from mpl_toolkits.mplot3d import Axes3D  # 绘制3D图形
from sklearn import metrics
import matplotlib


def KsNormDetect(df):
    # 计算均值
    u = df['money'].mean()
    # 计算标准差
    std = df['money'].std()
    # 计算P值
    res = kstest(df['money'], 'norm', (u, std))[1]
    # 判断p值是否服从正态分布，p<=0.05 则服从正态分布，否则不服从。
    if res <= 0.05:
        print('该列数据服从正态分布------------')
        print('均值为：%.3f，标准差为：%.3f' % (u, std))
        print('------------------------------')
        return 1
    else:
        return 0


def OutlierDetection(df, ks_res):
    # 计算均值
    u = df['money'].mean()
    # 计算标准差
    std = df['money'].std()
    if ks_res == 1:
        # 定义3σ法则识别异常值
        # 识别异常值
        error = df[np.abs(df['money'] - u) > 3 * std]
        # 剔除异常值，保留正常的数据
        data_c = df[np.abs(df['money'] - u) <= 3 * std]
        # 输出异常数据
        # print(error)
        return data_c

    else:
        print('请先检测数据是否服从正态分布-----------')
        return None


def data_filter(df):
    res = df[~df.category.isin(['教材供应中心', '小炒组', '校医院', '吧台', '一卡通中心'])]
    res = res[res.money > 0]
    res = res[~res.id.isin([87797269, 55867978778])]
    res = OutlierDetection(res, KsNormDetect(res))
    return res


def data_read():
    data = pd.DataFrame(columns=['time', 'category', 'money', 'id'])
    df = pd.read_excel('01.xlsx')
    data = data.append(df)
    df2 = pd.read_excel('02.xlsx')
    data = data.append(df2)
    df3 = pd.read_excel('03.xlsx')
    data = data.append(df3)
    return data


def date_processing(df):
    hour = df.copy(deep='true')
    hour['time'] = df['time'].dt.date
    day_ = hour[['time']]
    df['time'] = df['time'].dt.time
    df['day'] = day_['time']
    pan_1 = (df['time'] >= dt.time(5, 00, 00)) & (df['time'] < dt.time(10, 00, 00))
    pan_2 = (df['time'] >= dt.time(10, 00, 00)) & (df['time'] < dt.time(15, 00, 00))
    pan_3 = (df['time'] >= dt.time(15, 00, 00)) & (df['time'] < dt.time(21, 00, 00))
    pan_4 = (df['time'] >= dt.time(21, 00, 00)) & (df['time'] < dt.time(23, 00, 00))
    df.loc[pan_1, 'time'] = '早餐'
    df.loc[pan_2, 'time'] = '午餐'
    df.loc[pan_3, 'time'] = '晚餐'
    df.loc[pan_4, 'time'] = '宵夜'
    return df


def grouping(df):
    df = df.groupby(by=['id', 'day', 'time'], as_index=False)[['money']].sum()
    df = df[df['money'] > 1]
    df = df[(df['time'].isin(['早餐', '宵夜'])) | (df['money'] > 3)]
    return df


def features(df):
    money_v = df.groupby(['id']).apply(lambda x: list(x['money']))
    date_v = df.groupby(['id']).apply(lambda x: list(x['day']))
    features_money = []
    features_day = []
    for i in range(0, len(money_v)):
        first = 0
        second = 0
        three = 0
        third = 0
        eve = []
        for it in money_v[i]:
            if it >= 0 and it < 7:
                first += 1
            elif it < 13:
                second += 1
            elif it < 19:
                three += 1
            else:
                third += 1
        eve.append(first)
        eve.append(second)
        eve.append(three)
        eve.append(third)
        features_money += [eve]
        eve = []
        di = 0
        zhong = 0
        gao = 0
        pre = date_v[i][0]
        for j in range(1, len(date_v[i])):
            cur = date_v[i][j]
            dayss = (cur - pre).days
            if dayss >= 0 and dayss < 2:
                di += 1
            elif dayss < 5:
                zhong += 1
            else:
                gao += 1
            pre = cur
        eve.append(di)
        eve.append(zhong)
        eve.append(gao)
        features_day += [eve]
    return features_money, features_day  # 返回的是金额统计数据和间隔去食堂天数的统计


def pca_(day):
    pca = PCA(n_components=1)  # 把维度降至3维
    fdd = pca.fit_transform(preprocessing.scale(pd.DataFrame(day[1], columns=['f1', 'f2', 'f3'])))
    pca = PCA(n_components=2)  # 把维度降至3维
    fcost = pca.fit_transform(preprocessing.scale(pd.DataFrame(day[0], columns=['f1', 'f2', 'f3', 'f4'])))
    count = 0
    res = []
    for item in fcost:
        temp = np.append(item, fdd[count][0])
        res += [temp]
        count += 1
    return res


def scores(res):
    d = {}
    fig_reduced_data = plt.figure(
        figsize=(12, 12))  # 画图之前首先设置figure对象，此函数相当于设置一块自定义大小的画布，使得后面的图形输出在这块规定了大小的画布上，其中参数figsize设置画布大小
    for k in range(2, 14):
        est = KMeans(n_clusters=k, random_state=111)
        # 作用到降维后的数据上
        y_pred = est.fit_predict(res)
        # 评估不同k值聚类算法效果
        calinski_harabaz_score = metrics.calinski_harabasz_score(pd.DataFrame(res, columns=['f1', 'f2', 'f3']),
                                                                 y_pred)  # X_pca_frame：表示要聚类的样本数据，一般形如（samples，features）的格式。y_pred：即聚类之后得到的label标签，形如（samples，）的格式
        d.update({k: calinski_harabaz_score})
        print('calinski_harabaz_score with k={0} is {1}'.format(k, calinski_harabaz_score))  # CH score的数值越大越好
        # 生成三维图形，每个样本点的坐标分别是三个主成分的值
        ax = plt.subplot(4, 3, k - 1,
                         projection='3d')  # 将figure设置的画布大小分成几个部分，表示4(row)x3(colu),即将画布分成4x3，四行三列的12块区域，k-1表示选择图形输出的区域在第k-1块，图形输出区域参数必须在“行x列”范围
        ax.scatter(pd.DataFrame(res, columns=['f1', 'f2', 'f3']).f1, pd.DataFrame(res, columns=['f1', 'f2', 'f3']).f2,
                   pd.DataFrame(res, columns=['f1', 'f2', 'f3']).f3, c=y_pred)  # pca_1、pca_2、pca_3为输入数据，c表示颜色序列
        ax.set_xlabel('pca_1')
        ax.set_ylabel('pca_2')
        ax.set_zlabel('pca_3')
        if k == 10:
            plt.savefig('k-means_res.png', facecolor='white')


def get_score(d):
    x = []
    y = []
    for k, score in d.items():
        x.append(k)
        y.append(score)
    plt.plot(x, y)
    plt.xlabel('k value')
    plt.ylabel('calinski_harabaz_score')
    plt.savefig("k_scores.png", facecolor='white')

def kmeans_2(res):
    n_clusters = range(2, 3)
    for n in n_clusters:
        # 创建绘图区域
        fig, ax = plt.subplots(1)
        fig.set_size_inches(8, 6)

        # 实例化
        cluster = KMeans(n_clusters=n, random_state=10).fit(res)
        # 访问labels_属性，获得聚类结果
        y_pred = cluster.labels_
        # 访问cluster_centers_属性，获得质心坐标
        centroid = cluster.cluster_centers_
        # 计算平均轮廓系数
        silhouette_avg = silhouette_score(res, y_pred)

        # 绘制聚类结果
        # y_pred==i会返回布尔数组，从而获得那些被分为同一类的点
        for i in range(n):
            ax.scatter(res[y_pred == i, 0], res[y_pred == i, 1], marker='o', s=8, alpha=0.7)
            # 绘制质心
        ax.scatter(centroid[:, 0], centroid[:, 1], marker='x', s=30, c='k')
        # 设置图表标题
        ax.set_title('result of KMeans(n_clusters={})'.format(n))
        # 设置x轴标题
        ax.set_xlabel('money')
        # 设置y轴标题
        ax.set_ylabel('time')
        # 设置总标题，用来描述轮廓系数的值
        plt.suptitle('The average silhouette value is {:.4f}.'.format(silhouette_avg),
                     fontsize=14, fontweight='bold')

        plt.savefig('result of KMeans(n_clusters={})'.format(n))
        plt.show()