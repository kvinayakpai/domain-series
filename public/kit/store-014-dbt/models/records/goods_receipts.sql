select * from read_csv_auto('{{ var("data_dir") }}/goods-receipts-june.csv', types={'sscc': 'VARCHAR'})
