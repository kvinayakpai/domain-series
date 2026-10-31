select * from read_csv_auto('{{ var("data_dir") }}/pos-lines-may-june.csv', types={'gtin_scanned': 'VARCHAR'})
