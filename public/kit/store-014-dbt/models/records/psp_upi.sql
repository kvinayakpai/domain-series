select * from read_csv_auto('{{ var("data_dir") }}/psp-upi-report-june.csv', types={'rrn': 'VARCHAR', 'bill_ref': 'VARCHAR'})
