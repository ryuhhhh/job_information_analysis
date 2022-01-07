"""
メイン関数
"""
import argparse
import sys
sys.path.append('.')
sys.path.append('./get_data')
from company import workport as wp
import pandas as pd
import os
ENCODING = 'utf-8-sig'

def main(company_list,search_word,job_info_num,is_online=False):
    RIKUNAVI = 'rikunavi'
    WORKPORT = 'workport'
    DODA = 'doda'

    print(f'{company_list}を"{search_word}"で{job_info_num}件検索します。')

    abs_cur_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)))
    df_relative_path = f'/../got_data/workport_tokyo_{search_word}.csv'
    master_df_path = abs_cur_dir + df_relative_path
    if os.path.exists(master_df_path):
        job_info_df_master = pd.read_csv(master_df_path,encoding=ENCODING)
    else:
        job_info_df_master = pd.DataFrame()

    # 情報取得
    # [会社名,事業内容,勤務地,職種,仕事内容,応募資格(=求めている人材),勤務地,給与,URL]のリストで取得
    if WORKPORT in company_list:
        wp.wp_search_jobs(master_df_path,job_info_df_master,search_word,job_info_num,is_online)
    print('正常終了しました。')

if __name__ == "__main__":
    """
    args:
      get list: どの会社から求人情報を取得するか
    """

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--company-list', required=False, nargs="*", type=str, help='rikunavi workport doda',choices=['rikunavi', 'workport', 'doda'])
    parser.add_argument('--word', required=False, type=str, help='')
    parser.add_argument('--job-info-num', required=False, type=int, help='')
    parser.add_argument('--is-online',required=False,action='store_true')
    args = parser.parse_args()
    company_list = args.company_list
    search_word = args.word
    job_info_num = args.job_info_num
    is_online = args.is_online

    main(company_list,search_word,job_info_num,is_online)
