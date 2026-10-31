select * from read_csv_auto('{{ var("data_dir") }}/customer-complaints-june.csv', types={'rrn': 'VARCHAR'})
