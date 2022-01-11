# 概要
* 求人情報の会社情報・職務内容・募集要項を取得し解析します。その後、入力した文章と類似している解析された求人情報を取得します。
* イメージは下記となります。
  * 入力値: 適当な職務内容など
  * 出力値: 求人情報
* 求人情報の取得には数時間かかります。(取得先サーバへ負荷をかけない仕様のためです。)
* プログラム内では形態素解析後にTFIDF値を取得し、COS類似度を取得します。

# フォルダ構成(/BackEnd配下)
* got_data/
  * 下記のget_data/やtreat_data/で取得した値を格納するディレクトリです。
* get_data/
  * スクレイピングで求人情報を取得
* treat_data/
  * get_data/で取得したデータに対して形態素解析およびtfidf値を取得
* analyze/
  * 入力された文章を形態素解析およびTFIDF値を取得し、treat_data/で解析した文章と、その文章とのCOS類似度を算出し、似ている求人情報を出力
* routine/
  * 定期実行するプログラムを格納。get_data/およびtreat_data/を呼び出し、データをアップデートする。
* common/
  * 共通変数や処理

# 必要な準備
* MeCabや、それを扱うpythonのライブラリをインストール
* 必要に応じて下記などの単語をMeCabの辞書に追加
  * AIエンジニア
  * 統計解析
  * 統計検定
  * 未経験

# 処理の流れ および コマンド例
1. スクレイピングで求人情報を取得
   * python get_data/index.py --company-list workport --word エンジニア --job-info-num 100
2. 取得した求人情報を形態素解析およびTFIDF値を取得
   * python treat_data/index.py --job-type エンジニア --is-morphological-analysis --is-tfidf-analysis
3. 文章を入力し類似している求人情報を取得
   * python analyze/index.py  --job-type エンジニア --job-description "機械学習、ディープラーニング、モデルの構築、R&D" --qualification "未経験(ポテンシャル)OKだが、統計学や機械学習や数学の知識は必須。統計検定なおよし。"
   * 上記コマンド例では年収500万以上の求人を出力
