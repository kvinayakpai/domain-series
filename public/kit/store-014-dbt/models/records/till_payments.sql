select * from read_csv_auto('{{ var("data_dir") }}/pos-payments-june.csv', types={'rrn': 'VARCHAR', 'note': 'VARCHAR'})
