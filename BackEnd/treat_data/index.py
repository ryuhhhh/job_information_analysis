"""
get_data/で取得したデータを加工します。
・記号を置換
・形態素解析を実施
その結果をidそインデックスに保存します。
"""

import os
import sys
sys.path.append(os.path.join('..','common'))
sys.path.append(os.path.join('.','common'))
sys.path.append('.')
sys.path.append('..')
from common import util,const
import pandas as pd
import argparse
import pickle

def morphological_analysis(target_columns,df_len,result_path,file_path):
    count = 1
    CHUNK_SIZE = 100
    # 前処理結果格納用DF
    df_tmp = pd.DataFrame(columns=['id']).set_index('id', drop=False)
    print('形態素解析を開始')
    for job_info_chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE,encoding=const.ENCODING):
        print(f'{count*CHUNK_SIZE}/{df_len} to save')
        count+=1
        # cleaned_chunk = util.clean_text(job_info_chunk,target_columns)
        morphological_analysis_result_df = util.morphological_analysis_df(job_info_chunk,target_columns)
        df_tmp = pd.concat([df_tmp,morphological_analysis_result_df])
        df_tmp.to_csv(result_path)
    return df_tmp

def calculate_tf_idf(target_columns,df_len,file_path=f'./workport_tokyo_エンジニア_前処理後.csv'):
    """
    tf-idfを計算しその結果を集約したオブジェクトを返却
    """
    result_obj = {}
    for column in target_columns:
        tf_idf_result,feature_matrix = util.calculate_tf_idf(file_path,column,df_len)
        result_obj[column] = {
            'word_list':tf_idf_result.get_feature_names(),
            'idf':tf_idf_result.idf_,
            'feature_matrix':feature_matrix
        }
    return result_obj

def main(job_type,target_columns,is_morphological_analysis,is_tfidf_analysis):
    abs_cur_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)))

    df_relative_path = f'/../got_data/workport_tokyo_{job_type}.csv'
    master_df_file_path = abs_cur_dir + df_relative_path
    master_df = pd.read_csv(master_df_file_path,encoding=const.ENCODING)

    DF_LEN = len(master_df)
    csv_relative_path = f'/../got_data/workport_tokyo_エンジニア_前処理後.csv'
    RESULT_PATH = abs_cur_dir + csv_relative_path

    if is_morphological_analysis:
        morphological_analysis(target_columns,DF_LEN,RESULT_PATH,master_df_file_path)
    if is_tfidf_analysis:
        result_obj = calculate_tf_idf(target_columns,DF_LEN,RESULT_PATH)

        bin_relative_path = f'/../got_data/{const.TF_IDF_RESULT_FILE}'
        result_path = abs_cur_dir + bin_relative_path
        with open(result_path, 'wb') as f:
            pickle.dump(result_obj, f)
        print(f'{result_path}に保存しました。')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--job-type', required=True, type=str, help='',choices=['エンジニア', 'データサイエンティスト', 'AIエンジニア'])
    parser.add_argument('--target-text-list', required=False, nargs="*", type=str, help='',\
                        choices=const.TARGET_COLUMNS,\
                        default=const.TARGET_COLUMNS)
    parser.add_argument('--is-morphological-analysis', required=False,action='store_true')
    parser.add_argument('--is-tfidf-analysis',required=False,action='store_true')

    args = parser.parse_args()
    job_type = args.job_type
    target_columns = args.target_text_list
    is_morphological_analysis = args.is_morphological_analysis
    is_tfidf_analysis = args.is_tfidf_analysis

    main(job_type,target_columns,is_morphological_analysis,is_tfidf_analysis)