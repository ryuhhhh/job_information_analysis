"""
求人情報の内、下記を取得
・仕事内容
・求めている人材
・給与
@see https://www.workport.co.jp/robots.txt
User-agent: Bingbot
Crawl-delay: 15
"""
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import re
import const
import traceback

ENCODING = 'utf-8-sig'

def remove_tags_and_spaces(text):
    """
    タグやスペースを除去
    """
    tag_pattern = re.compile(r"<[^>]*?>")
    removed_text = tag_pattern.sub("", text).strip().replace('\u3000','')
    return removed_text

def wp_search_job_list(word,page_num):
    """
    求人情報のページ一覧を取得
    args:
      word: 検索文字列
      n: ページNo.
    """
    url = f"https://www.workport.co.jp/all/search/area-23/word-{word}/?p={page_num}#cnt"
    link_list = []
    try:
        html = requests.get(url)
    except Exception as ex:
        print(f'{url}先が見つかりませんでした。終了します。')
        print(traceback.format_exc())
        return link_list
    html.encoding = "UTF-8"
    soup = BeautifulSoup(html.text, "html.parser")
    h2_list = soup.find_all("h2",attrs={"class": "mttl"})
    for h2 in h2_list:
        # hrefを持つaタグを持つh2のurlを取得
        if h2.a.has_attr('href'):
            link_list.append(h2.a['href'])
    return link_list

def wp_get_job_info_description(job_link):
    """
    求人情報詳細を取得
     1. 会社名
     2. 事業内容
     3. 仕事内容
     4. 職種
     5. 応募資格(=must)
     6. 求めるスキル
     7. 勤務地
     8. 給与
     9. URL
    """
    url = f"https://www.workport.co.jp{job_link}"
    try:
        html = requests.get(url)
    except Exception as ex:
        print(traceback.format_exc())
        print(f'{job_link}が見つかりませんでした。終了します。')
        return None
    html.encoding = "UTF-8"
    soup = BeautifulSoup(html.text, "html.parser")
    job_obj = {}

    # 1.会社名 h1 cmpname
    company_name = soup.find('p',attrs={"class": "cmpname"}).text
    if company_name:
        job_obj[const.COMPANY_NAME] = company_name

    # 4.職種 p mttl
    job_name = soup.find('h1',attrs={"class": "mttl"}).text
    if job_name:
        job_obj[const.JOB_NAME] = job_name

    # 職務概要,職務詳細,会社の特徴 を探す
    job_summary = soup.find('div',attrs={"class":"jobSummaryInTop is-dettop"})

    ## ジョブサマリを<b>{タイトル}</b>区切りでリストに分割(タグの値もリストに含む)
    pattern = re.compile(r'(<b>\w*</b>)')
    JOB_SUMMARY = '職務概要'
    JOB_DESCRIPTION = '職務詳細'
    EXPECTED_POSITION = '想定されるポジション'
    COMPANY_FEATURES = '会社の特徴'
    b_tag_titles = [JOB_SUMMARY,EXPECTED_POSITION,JOB_DESCRIPTION,COMPANY_FEATURES]
    result_list = pattern.split(str(job_summary))

    NOT_FOUND_INDEX = -1
    get_index = NOT_FOUND_INDEX
    for result in result_list:
        ## 対象のタイトル名が見つかった場合
        if get_index != NOT_FOUND_INDEX:
            # タグ及び全角空白を削除
            illminate_result = remove_tags_and_spaces(result)
            job_obj[b_tag_titles[get_index]] = illminate_result
            get_index = NOT_FOUND_INDEX
            continue
        ## タイトルが含まれるかどうか操作
        for index,title in enumerate(b_tag_titles):
            ## 含まれる場合次のresultのループでは値を取得できる
            if title in result:
                get_index = index
                continue

    # 2.事業内容(会社の特徴)
    if COMPANY_FEATURES in job_obj:
        job_obj[const.COMPANY_INFO] = job_obj.pop(COMPANY_FEATURES)

    # 3.仕事内容
    job_description = ''
    for value in b_tag_titles:
        if value in job_obj:
            job_description += job_obj.pop(value)
    job_obj[const.JOB_DESCRIPTION] = job_description

    # dlタグにdt(タイトル)とdd(内容)が入っている
    job_summary_below = soup.find('div',attrs={"class":"recruitcov2"})
    OUBO_SHIKAKU = '応募資格'
    MOTOMERU_SKILL = '求めるスキル'
    KINMUTI = '勤務地'
    SOUTEI_KYUYO = '想定給与'

    # 5.応募資格
    qualification = job_summary_below.find('dt',text=OUBO_SHIKAKU)
    if qualification:
        job_obj[const.QUALIFICATION] =\
            remove_tags_and_spaces(qualification.next_sibling.next_sibling.text)

    # 6.求めるスキル
    skills = job_summary_below.find('dt',text=MOTOMERU_SKILL)
    if skills:
        job_obj[const.SKILLS] = \
            remove_tags_and_spaces(skills.next_sibling.next_sibling.text)

    # 7.勤務地
    location = job_summary_below.find('dt',text=KINMUTI)
    if location:
        job_obj[const.JOB_LOCATION] = \
            remove_tags_and_spaces(location.next_sibling.next_sibling.text)

    # 8.想定給与
    salary_pattern = re.compile(r'(\d+)万円～(\d+)万円')
    salary = job_summary_below.find('dt',text=SOUTEI_KYUYO)
    if salary:
        salary = \
            remove_tags_and_spaces(salary.next_sibling.next_sibling.text)
        salary_find_result = salary_pattern.match(salary).groups(0)
        job_obj[const.SALARY_FROM] = int(salary_find_result[0])
        job_obj[const.SALARY_TO] = int(salary_find_result[1])

    # 9.url
    job_obj[const.URL] = url

    # ID
    hyphen_url = url.replace('/','-')
    ## URLより数字-数字を抜き出す
    id_search_obj = re.search(r'\d+\-\d+',hyphen_url)
    if not id_search_obj:
        # hikoukai-{数字}のパターン
        id_search_obj = re.search(r'\w+\-\d+',hyphen_url)
    id = id_search_obj.group()

    job_obj[const.ID] = id

    return job_obj

def save_df_online_or_ofline(is_online,master_df,job_info_df,path):
    MAX_DF_NUM = 10000
    concat_list = [master_df,job_info_df]
    if is_online:
        concat_list = [job_info_df,master_df]
    master_df = pd.concat(concat_list)
    master_df[:MAX_DF_NUM].to_csv(path,encoding = ENCODING)


def wp_search_jobs(master_df_path,master_df,word,job_info_num,is_online=False):
    """
    求人情報のページ一覧を取得し,
    各一覧ページより詳細な仕事情報を取得
    args:
      word: 検索文字列
      job_info_num: 求人情報取得数
    """
    job_info_df = pd.DataFrame(columns=['id',const.COMPANY_NAME]).set_index('id', drop=False)
    double_check_flg = False
    if not master_df.empty:
        double_check_master_df = master_df['id'][:50]
        double_check_flg = True

    job_info_count = 0 # 求人情報検索数
    pre_list_num = 0
    list_num = 0
    page_num = 1
    # デフォルトで30件ずつ表示
    display_num = 30
    CSV_PARTIAL_NUM = 2000
    csv_suffix = f'{len(master_df)}_{len(master_df)+CSV_PARTIAL_NUM}'
    doubled_search_num = 0

    while True:
        print(f'{page_num}ページ目_{display_num*(page_num-1)}~{display_num*(page_num)}')
        # ログ設定

        # 求人情報の一覧を取得
        link_list = wp_search_job_list(word,page_num)
        list_num = len(link_list)
        # 最後のページまで移動したら
        if pre_list_num > list_num:
            print(f'取得できないため3sスリープ {page_num}ページ目')
            time.sleep(3)
            continue
        pre_list_num = list_num
        page_num += 1
        time.sleep(1)

        # 求人情報一覧をループし各詳細情報を取得
        for job_link in link_list:
            print(f'{page_num-1} - {job_info_count}: {job_link}を検索')
            job_obj = wp_get_job_info_description(job_link)
            job_info_count += 1
            # 値を直近の50件より検索し存在(=既に取得済み)したら終了
            if double_check_flg and job_obj:
                doubled_search_num = (double_check_master_df == job_obj['id']).sum()
            if doubled_search_num:
                break
            print('2重チェック問題なし')
            # 検索結果を逐一保存
            job_info_df = job_info_df.append(job_obj,ignore_index=True)
            job_info_df.to_csv(f'./workport_tokyo_{word}_tmp_{csv_suffix}.csv',encoding = ENCODING)
            if len(job_info_df) >= CSV_PARTIAL_NUM:
                print(f'{CSV_PARTIAL_NUM}まで達したので分割します。')
                # 保存
                save_df_online_or_ofline(is_online,master_df,job_info_df,master_df_path)
                # 初期化
                job_info_df = pd.DataFrame(columns=['id',const.COMPANY_NAME])
                job_info_df = job_info_df.set_index('id', drop=False)
                # tmpファイルの接尾語を変更
                str_partial_num_len = len(str(CSV_PARTIAL_NUM))
                csv_suffix = f'{csv_suffix[-str_partial_num_len:]}_{int(csv_suffix[-str_partial_num_len:])+CSV_PARTIAL_NUM}'
            print('保存しました')
            # サーバ負荷対策
            time.sleep(1)

        if doubled_search_num:
            print('2重に検索(過去に検索済み)のため保存して終了します。')
            save_df_online_or_ofline(is_online,master_df,job_info_df,master_df_path)
            break

        # 最大取得数まで来たら
        if job_info_count >= job_info_num:
            print(f'{job_info_num}件検索したため終了します。')
            save_df_online_or_ofline(is_online,master_df,job_info_df,master_df_path)
            break
        job_info_count += 1
    print('終了しました')
    return master_df
