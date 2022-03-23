python kaggle_dataset_collect.py

FILE="datasets.json"
if [ -f $FILE ];then
  echo "file exists"
  rm $FILE
fi
wget https://production-media.paperswithcode.com/about/datasets.json.gz
gzip -d datasets*

python paperwithcode_dataset_collect.py
python index_generator.py --stemming True --remove_stopwords True --local_kaggle_dataset kaggle_dataset_df_page500.csv --local_paperwithcode_dataset paperwithcode_df.csv

