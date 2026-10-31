select * from read_csv_auto('{{ var("data_dir") }}/shipping-notice-lines-june.csv', types={'sscc': 'VARCHAR', 'gtin': 'VARCHAR'})
