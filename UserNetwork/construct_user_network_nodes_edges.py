import pandas as pd
import datetime
import time
import argparse
import re
import networkx as nx
import matplotlib.pyplot as plt
from newspaper import Article

import utils_db



def Newslogs_preprocessing(Newslogs):
    def clean_url(article_url):
        def clean_CHT_url(url):
            if '?chdtv' in url: url = url.replace('?chdtv', '')
            if '?ctrack' in url: url = url[:url.find('?ctrack')]
            return url
        def clean_LBT_url(url):
            if '?utm_source' in url: url = url[:url.find('?utm_source')]
            return url
        if 'chinatimes.com/' in article_url: return clean_CHT_url(article_url)
        if 'ltn.com.tw/' in article_url: return clean_LBT_url(article_url)
    
    Newslogs = [[clean_url(k[0]), k[1], k[2], k[3]] for k in Newslogs]
    Newslogs.reverse()
    return Newslogs


def create_user_network_nodes(Newslogs, USERINDEX, TODAY_DATE):
    def check_parse_news_details_or_not(article_url) -> bool:
        """Check whether the url is linked to a news or not.
           It returns a bool ->
               True: If the url linked to a news.
               False: If the url doesnt linked to a news, such as a frontpage.
        """
        if 'ltn.com.tw/' in article_url:
            if re.match('https://([a-z]*?).ltn.com.tw/(.*?)/(\d{7})', article_url)!=None:
                return True
            else:
                print('***PAGE NOT NEED DETAILS***\n', article_url)
                return False
        elif 'chinatimes.com/' in article_url:
            def clean_CHT_url(url):
                if '?chdtv' in url: url = url.replace('?chdtv', '')
                if '?ctrack' in url: url = url[:url.find('?ctrack')]
                return url
            article_url = clean_CHT_url(article_url)
            if re.match('https://www.chinatimes.com/(.*?)/(\d{14}-\d{6})', article_url)!=None:
                return True
            else:
                print('***PAGE NOT NEED DETAILS***\n', article_url)
                return False
            
    def get_news_details(article_url, NEWSINDEX, TODAY_DATE):
        """Parse News details, including NewsUrl, PublishDate, NewsTitle and NewsContent.
           It returns
               a list -> news_details: [NewsIndex, ParseDate, NewsUrl, PublishDate, NewsTitle, NewsContent]
               and an int -> NEWSINDEX: Records the NewsIndex
        """
        if check_parse_news_details_or_not(article_url)==True:
            article = Article(article_url)
            try:
                print('***DOWNLOADING***\n', article_url)
                article.download()
                article.parse()
            except:
                print('***FAILED TO DOWNLOAD***\n', article_url)
                return False
            article_date = str(article.publish_date)[:10]

            NEWSINDEX+=1
            news_details = [USERINDEX+'_'+str(NEWSINDEX), TODAY_DATE, article_url, article_date, article.title, article.text]
            return news_details, NEWSINDEX

        elif check_parse_news_details_or_not(article_url)==False:
            news_details = [article_url, TODAY_DATE, article_url, '', '', '']
            return news_details, NEWSINDEX
        
        
    NEWSINDEX = 0
    user_network_nodes = []
    ### 抓出瀏覽紀錄中不重複的 url
    Newslogs_unique_urls = []
    for log in Newslogs:
        if log[0] not in Newslogs_unique_urls:
            Newslogs_unique_urls.append(log[0])
    ### 針對不重複的 url
    ### 爬取瀏覽新聞的詳細資料（新聞編號、新聞網址、新聞撰寫日期、新聞標題、新聞內文）
    for article_url in Newslogs_unique_urls:
        news_details, NEWSINDEX = get_news_details(article_url, NEWSINDEX, TODAY_DATE)
        user_network_nodes.append(news_details)
    return user_network_nodes


def create_user_network_edges(Newslogs, user_network_nodes):
    user_network_edges = []
    for i in range(0, len(Newslogs)-1):
        url_1 = Newslogs[i][0]
        url_2 = Newslogs[i+1][0]
#         print('-'*50+'\n%s\n%s' %(url_1, url_2))
        user_network_nodes_urls = [k[2] for k in user_network_nodes]
        if url_1 in user_network_nodes_urls and url_2 in user_network_nodes_urls:
            c1 = user_network_nodes[user_network_nodes_urls.index(url_1)][0]
            c2 = user_network_nodes[user_network_nodes_urls.index(url_2)][0]
            
            ### 取比較大的時間作為瀏覽時間
            d1 = datetime.datetime.strptime(Newslogs[i][2], "%Y-%m-%d %H:%M:%S")
            d2 = datetime.datetime.strptime(Newslogs[i+1][2], "%Y-%m-%d %H:%M:%S")
            if d1>=d2: parse_date=Newslogs[i][2]
            else: parse_date=Newslogs[i+1][2]
            
            user_network_edges.append([c1, c2, parse_date])
#             print(c1, c2)
    return user_network_edges


def draw_network(nodes, edges, TODAY_DATE):
    G = nx.Graph() 
    G.add_nodes_from(nodes) 
    G.add_edges_from(edges)
    nx.draw(G,
            pos = nx.spring_layout(G),
            node_color = 'blue',
            edge_color = 'black',
            with_labels = True,
            font_size =5,
            node_size =40)
    plt.savefig('./Networks_png/Network_%s.png' %(TODAY_DATE), dpi=300)
#     plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get news browsing history.')
    parser.add_argument('--browser_history_path', '-i', default='./firefox_history.csv', help='Path to firefox/chrome_history.csv file')
    parser.add_argument('--db_path', '-o', default='./user2.db', help='Path to database which records user network nodes and edges')
    parser.add_argument('--username', '-u', required=True, help='Input username')
    args = parser.parse_args()
    
    Newslogs = pd.read_csv(args.browser_history_path, encoding='utf8', header=0).values.tolist() 
    Newslogs = Newslogs_preprocessing(Newslogs)
    TODAY_DATE = time.strftime('%Y-%m-%d',datetime.datetime.timetuple(datetime.datetime.now()))
    USERINDEX = args.username #'user2' 
    
    # 從瀏覽紀錄中建立網路圖的 nodes
    user_network_nodes = create_user_network_nodes(Newslogs, USERINDEX, TODAY_DATE)
    # 從瀏覽紀錄中建立網路圖的 edges
    user_network_edges = create_user_network_edges(Newslogs, user_network_nodes)
    
    # 輸出結果至 sqlite3 資料庫中
    utils_db.insert_nodes_table(args.db_path, user_network_nodes)
    utils_db.insert_edges_table(args.db_path, user_network_edges)
    
    # 利用 networkx 畫出「瀏覽紀錄網路圖」
    draw_network(nodes=[k[0] for k in user_network_nodes], edges=[[k[0], k[1]] for k in user_network_edges], TODAY_DATE=TODAY_DATE)

