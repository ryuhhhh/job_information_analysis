import argparse
import pandas as pd
import os
import pickle
import sys
sys.path.append('.')
from common import util
from common import const
import numpy as np

def calculate_tf_idf_from_text(text_obj,tfidf_path):
    """
    文字列を渡したときにそのtf-idf値を計算し
    上位10件を返却
    """
    with open(tfidf_path, 'rb') as f:
        tf_idf = pickle.load(f)
    cos_sim_result_obj = {}
    for key,text in text_obj.items():
        if not text:
            continue
        morphological_analysis_result = util.morphological_analysis(text)
        # textを形態素解析し単語ごとに区切る
        noun_list = util.get_noun_list_from_mecab_result(morphological_analysis_result)
        # tfを算出
        tf_obj = {}
        for noun in noun_list:
            tf_obj[noun] = noun_list.count(noun) / len(noun_list)
        # idfを取得
        idf_words = tf_idf[key]['word_list']
        idf_values = tf_idf[key]['idf']
        # tf-idfベクトルを取得(1 x 単語数)
        tfidf_vec = calculate_tfidf(tf_obj,idf_words,idf_values)
        # TF-IDFの結果を取得(文書数x単語数で作成されている)
        feature_matrix = tf_idf[key]['feature_matrix']
        # cos類似度を求める [1 x 単語数] と [単語数 x 全文書数]
        cos_sim_result = calculate_cos_similarity(tfidf_vec,feature_matrix.T)
        cos_sim_result_obj[key] = cos_sim_result

    return cos_sim_result_obj

def calculate_tfidf(tf_obj,idf_words,idf_values):
    tfidf_list = np.array([])
    for index,word in enumerate(idf_words):
        if word not in tf_obj:
            tfidf_list = np.append(tfidf_list,0)
            continue
        tfidf_value = tf_obj[word] * idf_values[index]
        tfidf_list = np.append(tfidf_list,tfidf_value)
    return tfidf_list

def calculate_cos_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def main(job_type,job_description,qualification,company_info,salary):
    # csv読み込み
    abs_cur_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)))
    df_relative_path = f'/../got_data/workport_tokyo_{job_type}.csv'
    tfidf_relative_path = f'/../got_data/{const.TF_IDF_RESULT_FILE}'
    master_df_path = abs_cur_dir + df_relative_path
    tfidf_path = abs_cur_dir + tfidf_relative_path
    if os.path.exists(master_df_path):
        job_info_df = pd.read_csv(master_df_path,encoding=ENCODING)
    else:
        print('ファイルが存在しません。')
        exit()

    cos_sim_result_obj = calculate_tf_idf_from_text({'job_description':job_description,\
                                             'qualification':qualification,\
                                             'company_info':company_info},\
                                             tfidf_path)

    # リストへ結果の積を求めていく。最初の値として1を指定。
    all_crossed_list = 1
    # 年収でフィルタ
    for key,item in cos_sim_result_obj.items():
        if not len(item):
            continue
        # 全要素を掛け算
        all_crossed_list *= item

    # 結果を類似度上位10件返却する
    RESULT_RANK_NUM = 10
    result_rank_list = []
    for i in range(RESULT_RANK_NUM):
        target_row_num = np.argsort(all_crossed_list)[::-1][i]
        result_rank_list.append(target_row_num)

    # 上位10件抜き出して年収でフィルタ
    target_df_rows = job_info_df.iloc[result_rank_list]
    salary_filterd_target_df = target_df_rows[target_df_rows['salary_from']>=salary]

    # 結果出力
    for index,row in salary_filterd_target_df.iterrows():
        print(f'------')
        print(f'会社名: {row["company_name"]}\n\
                求人名: {row["job_name"]}\n\
                給与: {row["salary_from"]}~{row["salary_to"]}\n\
                URL: {row["url"]}')
        print(f'------')

    return salary_filterd_target_df

if __name__ == "__main__":
    """
    分析メイン関数
    指定の求人IDの文章と他の求人の類似度を算出
    高い順に最大100件返却
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--job-type', required=True, type=str, help='',choices=['エンジニア', 'データサイエンティスト', 'AIエンジニア'])
    parser.add_argument('--job-description', required=False, type=str, help='')
    parser.add_argument('--qualification', required=False, type=str, help='')
    parser.add_argument('--company-info', required=False, type=str, help='')
    parser.add_argument('--salary', required=False, type=int, help='',default=0)
    args = parser.parse_args()
    job_type = args.job_type
    job_description = args.job_description
    qualification = args.qualification
    company_info = args.company_info
    salary = args.salary
    ENCODING = 'utf-8-sig'

    # 求人情報の職務情報や
    main(job_type,job_description,qualification,company_info,salary)
