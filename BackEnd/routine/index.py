"""
定期的に情報を取得し、
tf-idf値を更新していきます。
・情報取得 - /get_data/index.py
・形態素解析&tf-idf値取得 - /treat_data/index.py
"""

import sys
sys.path.append('.')
sys.path.append('..')
from get_data import index as gd
from treat_data import index as td
from common import const

def main():
    # データをオンライン(差分)取得
    gd.main(company_list=['workport'],search_word='エンジニア',job_info_num=10000,is_online=True)
    # 形態素解析およびtfidfを算出実施
    td.main(job_type='エンジニア',target_columns=const.TARGET_COLUMNS,is_morphological_analysis=True,is_tfidf_analysis=True)

if __name__ == '__main__':
    main()