#
#—爬取搜狗输入法的医学词库，下载.scel格式文件
#
#参考代码 原文链接：https://blog.csdn.net/Q_QuanTing/article/details/82698229

#encoding:UTF-8
from bs4 import BeautifulSoup
import requests
import time
import json
import re
import urllib.parse 
from tqdm import tqdm

def get_cate_list(res_html):
    """
    获取https://pinyin.sogou.com/dict/cate/index/132/default/ 下的

      “基础医学(39)	西药学(52)	中医(71)	中药(42)	针灸(2)	疾病(18)	超声医学(5)
    耳鼻喉科(3)	法医学(2)	护理学(4)	解剖学(12)	口腔医学(9)	美容外科(11)	皮肤科(8)
    兽医(5)	医疗器械(19)	医学影像学(5)	肿瘤形态学(1)	医学检验(3)	医疗(32)	外科(8)
    其它(41)”    
    
    的超链接。
    """
    # 获取第二种小分类链接
    dict_cate_dict = {}
    soup = BeautifulSoup(res_html, "lxml")
    dict_td_lists = soup.find_all("div", class_="cate_no_child no_select")
    # 类型1解析
    for dict_td_list in dict_td_lists:
        dict_td_url = "https://pinyin.sogou.com" + dict_td_list.a['href']
        dict_cate_dict[dict_td_list.get_text().replace("\n", "")] = dict_td_url

    return dict_cate_dict


def get_page(res_html):
    """
    获取主题页数
    """
    # 页数
    soup = BeautifulSoup(res_html, "html.parser")
    dict_div_lists = soup.find("div", id="dict_page_list")
    dict_td_lists = dict_div_lists.find_all("a")
    if dict_td_lists == []:
        return 1
    else:
        page = dict_td_lists[-2].string
        return int(page)


def get_download_list(res_html):
# 获取当前页面的下载链接
    dict_dl_dict = {}
    pattern = re.compile(r'name=(.*)')
    soup = BeautifulSoup(res_html, "html.parser")
    dict_dl_lists = soup.find_all("div", class_="dict_dl_btn")
    for dict_dl_list in dict_dl_lists:
        dict_dl_url = dict_dl_list.a['href']
        dict_name = pattern.findall(dict_dl_url)[0]
        dict_ch_name = urllib.parse.unquote(dict_name, 'utf-8').replace("/", "-").replace(",", "-").replace("|", "-")\
            .replace("\\", "-").replace("'", "-")
        dict_dl_dict[dict_ch_name] = dict_dl_url
    return dict_dl_dict


def download_dict(dl_url, path):
    # 下载
    res = requests.get(dl_url, timeout=5)
    #print(res)
    #print(res.content)
    with open(path, "wb") as fw:
        fw.write(res.content)


def get_html(res):
    r = requests.get(res)
    content = r.text
    return content
        

if __name__ == "__main__":

    res = 'https://pinyin.sogou.com/dict/cate/index/132/default/' #大类地址
    content = get_html(res)
    address = get_cate_list(content) 
    
    downloadlist = []
    for ad in tqdm(address):

        print("Get {} ".format(ad))

        res = address[ad] #获取子类的地址 
        c = get_html(res) #获取子类页面
        pages = get_page(c) #获取子类页面页数
        
        for i in range(pages):
            if i + 1 == 1:
                d = get_download_list(c)
            else:
                d = get_download_list(c + '/default/' + str(i + 1))
            downloadlist.append(d)
        
    print(downloadlist) #获取所有词库的下载地址

    print("Downloading...")
    s = 0 #词库个数
    scel_path = "E:\\lixiang\\nlp code\\datasets\\医学词汇\\scel_bank\\"
    for j in range(len(downloadlist)):
        for sub_d in tqdm(downloadlist[j]):
            s = s + 1
            print(s)
            download_dict(downloadlist[j][sub_d], scel_path + sub_d + '.scel')

