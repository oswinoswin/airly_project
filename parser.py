import os
import ast
import pprint
import pandas as pd

result = pd.DataFrame()
index = []
columns = []
for directory in filter(lambda dir: dir.startswith('2018'), next(os.walk('.'))[1]):
	day_result = None
	for filename in os.listdir(directory):
		if filename.endswith('.txt'):
			with open(os.path.join(directory, filename), 'r') as f:
				print(directory, filename)
				content = ast.literal_eval(f.read())
				try:
					index = [x['fromDateTime'][:-1] for x in content['history']]
					columns = ['UTC time'] + [filename[:-4] + "_" + y['name'].lower() for y in content['history'][0]['values']]
					if day_result is None:
						day_result = pd.DataFrame(index=index)
					df = pd.DataFrame(columns=columns)
					for idx, x in enumerate(content['history']):
						df = df.append(pd.DataFrame([[y['value'] for y in x['values']]],index=[index[idx]], columns=columns))
					day_result = pd.merge(day_result, df, left_index=True, right_index=True, how='inner')
				except:
					pass
	result = result.append(day_result)	
result.sort_index(inplace=True)	
result.to_csv('data2.csv', sep=',', encoding='utf-8', quotechar='"', decimal='.', mode='a')
