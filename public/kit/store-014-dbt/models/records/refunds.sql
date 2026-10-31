select * from read_csv_auto('{{ var("data_dir") }}/upi-refunds-june.csv', types={'rrn': 'VARCHAR'})
