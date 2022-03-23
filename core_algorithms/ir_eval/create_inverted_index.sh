python core_algorithms/ir_eval/kaggle_dataset_collect.py

FILE= "datasets.json"
if [ -f $FILE ];then
  echo "file exists!"
  rm -f datasets.json
fi
wget https://production-media.paperswithcode.com/about/datasets.json.gz
gzip -d datasets*
python core_algorithms/ir_eval/paperwithcode_dataset_collect.py
python core_algorithms/ir_eval/edinburghexplorer.py 
python core_algorithms/ir_eval/uci_dataset_collect.py

create inverted index
python core_algorithms/ir_eval/index_generator.py --stemming True --remove_stopwords True \
--local_kaggle_dataset core_algorithms/ir_eval/kaggle_dataset_df_page500.csv \
--local_paperwithcode_dataset core_algorithms/ir_eval/paperwithcode_df.csv \
--local_uci_dataset core_algorithms/ir_eval/uci_dataset_test.csv \
--local_edi_dataset core_algorithms/ir_eval/edinburgh_research_datasets_info.csv
