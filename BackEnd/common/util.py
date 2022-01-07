import pandas as pd
import MeCab
import sys
sys.path.append('..')
from common import const

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def save_df(df,sub_df,file_path,encoding='utf-8-sig'):
    df = pd.concat([df,sub_df])
    df.to_csv(file_path,encoding=encoding)

def clean_text(df,target_columns):
    """
    形態素解析結果から記号などを除去
    ・大文字を小文字に
    ・数字-記号-数字なら記号を除去して結合
    ・記号-文字 または 文字-記号 なら記号を除去
    """
    symbol_list = ['★','・','！','!','▼','〜','，','”','■','☆','◆','●','□','+','-','】','『','』','【','】','※','、','（','）','.']
    # for symbol in symbol_list:
    #     job_info_df[target_columns] = job_info_df[target_columns].replace(f'\{symbol}',"",regex=True)
    # 文字を置換
    df[target_columns] = df[target_columns].values.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
    return df

def morphological_analysis_df(job_info_df,target_columns):
    """
    形態素解析を実施し、その結果を返却
    """
    result_df = pd.DataFrame(columns=['id',*target_columns])
    for index,row in job_info_df.iterrows():
        row_obj = {}
        for column in target_columns:
            if pd.isna(row[column]):
                continue
            # result = mecab.parse(row[column])
            result = morphological_analysis(row[column])
            noun_list = get_noun_list_from_mecab_result(result)
            nouns = '|'.join(noun_list)
            row_obj[column] = nouns
        row_obj[const.ID] = row[const.ID]
        result_df = result_df.append(row_obj,ignore_index=True)
    return result_df

def morphological_analysis(text,mecab=None):
    if not mecab:
        mecab = MeCab.Tagger("-r C:\\PROGRA~1\\MeCab\\etc\\mecabrc-u")
    return mecab.parse(text)

def get_noun_list_from_mecab_result(result):
    TARGET_KEY = '名詞'
    noun_list =[ line.split()[0]\
                 for line in result.splitlines()\
                     if TARGET_KEY in line]
    return noun_list

def calculate_tf_idf(file_path,target_column,df_len):
    """
    tf-idf値を計算
    """
    print('tf-idf値を計算')
    # ドキュメントのリストをチャンクとして渡すための準備
    corpus  = ChunkIterator(file_path,target_column,df_len)
    tfidf = TfidfVectorizer()
    result = tfidf.fit_transform(corpus)
    return tfidf,result.toarray()

def ChunkIterator(file_path,target_column,df_len):
    count = 1
    CHUNK_SIZE = 100
    for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE):
      print(f'{count*CHUNK_SIZE}/{df_len}')
      count += 1
      for doc in chunk[target_column].values:
          if pd.isna(doc):
              doc = ''
          doc = doc.replace('|',' ')
          yield doc

