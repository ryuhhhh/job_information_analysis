import argparse
import pandas as pd
import os
import pickle
import sys
sys.path.append(os.path.join('..', 'common'))
import util
import const
import numpy as np

def calculate_tf_idf_from_text(text_obj):
    """
    文字列を渡したときにそのtf-idf値を計算
    """
    with open(f'./../../{const.TF_IDF_RESULT_FILE}', 'rb') as f:
        if_idf = pickle.load(f)
    for key,text in text_obj.items():
        if not text:
            continue
        morphological_analysis_result = util.morphological_analysis(text)
        # textを形態素解析し単語ごとに区切る
        noun_list = util.get_noun_list_from_mecab_result(morphological_analysis_result)
        # tfを取得
        tf_obj = {}
        for noun in noun_list:
            tf_obj[noun] = noun_list.count(noun) / len(noun_list)
        # idfを取得
        idf_words = if_idf[key]['word_list']
        idf_values = if_idf[key]['idf']
        # tf-idfベクトルを取得(1x単語数)
        tfidf_vec = calculate_tfidf(tf_obj,idf_words,idf_values)
        # TF-IDFの結果を取得(文書数x単語数で作成されている)
        feature_matrix = if_idf[key]['feature_matrix']
        # cos類似度を求める [1 x 単語数] と [単語数 x 全文書数]
        cos_sim_result = calculate_cos_similarity(tfidf_vec,feature_matrix.T)
        for i in range(len(cos_sim_result)):
            if i>3:
                break
            print (np.argsort(cos_sim_result)[::-1][i], np.sort(cos_sim_result)[::-1][i])

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

    # csv読み込み
    master_df_path = f'./../../workport_tokyo_{job_type}.csv'
    if os.path.exists(master_df_path):
        job_info_df = pd.read_csv(master_df_path,encoding=ENCODING)
    else:
        print('ファイルが存在しません。')
        exit()

    # 年収で絞り込み
    if salary:
        job_info_df = job_info_df[job_info_df['salary_from']>salary]

    calculate_tf_idf_from_text({'job_description':job_description,\
                                'qualification':qualification,\
                                'company_info':company_info})
