select * from read_csv_auto('{{ var("data_dir") }}/products.csv', types={'gtin': 'VARCHAR'})
