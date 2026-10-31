select * from read_csv_auto('{{ var("data_dir") }}/pallets-june.csv', types={'sscc': 'VARCHAR'})
