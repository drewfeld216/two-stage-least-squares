import os
import pandas as pd
from statsmodels.sandbox.regression.gmm import IV2SLS
import statsmodels.api as sm
import numpy as np


def getColsAsIterable(filename):
	if '.csv' in filename:
		df_file = pd.read_csv(filename)
		
	elif '.xlsx' in filename:
		df_file = pd.read_excel(filename)
		
	cols = list(df_file.columns)
	count = list(range(len(cols)))
	out = [(col, i) for col, i in zip(cols, count)]
		
	return out

def runRegression(filepath, data_dict):
	if '.csv' in filepath:
		data = pd.read_csv(filepath)
	elif '.xlsx' in filepath:
		data = pd.read_excel(filepath)
		
	data_cols = list(data.columns)
	
	dep_cols = [ data_cols[i] for i in range(len(data_cols)) if i in data_dict['dep'] ]	
	endog_cols = [ data_cols[i] for i in range(len(data_cols)) if i in data_dict['endog'] ]	
	exog_cols = [ data_cols[i] for i in range(len(data_cols)) if i in data_dict['exog'] ]
	instr_cols = [ data_cols[i] for i in range(len(data_cols)) if i in data_dict['instr'] ]
		
	print
		
	if len(dep_cols) > 1:
		raise IndexError
		
	if (len(instr_cols) != len(endog_cols)) and len(instr_cols) > 0:
		raise ValueError
		
		
	dep = data[dep_cols].to_numpy()
	endog = data[endog_cols].to_numpy()
	exog = data[exog_cols].to_numpy()
	instr = data[instr_cols].to_numpy()
	
	const = np.ones(dep.shape)
	
	exog_comb = np.concatenate([exog, endog, const], axis=1)
	instr_comb = np.concatenate([exog, instr, const], axis=1)
		
	x_cols = exog_cols + endog_cols
	x_cols.append('const')

	if len(instr_cols) == 0:
		mod = sm.OLS(dep, exog_comb)
		reg = mod.fit()

		summ = reg.summary(yname=dep_cols[0], xname=x_cols)
		output = getOLSOutputTable(summ)
		output += copyButton()
		return output
	
	else:
		mod_2sls = IV2SLS(dep, exog_comb, instr_comb)
		reg_2sls = mod_2sls.fit()
		summ_2sls = reg_2sls.summary(yname=dep_cols[0], xname=x_cols)
		output = get2SLSOutputTable(summ_2sls)
				
		mod_ols = sm.OLS(endog, instr_comb)
		reg_ols = mod_ols.fit()
		ols_cols = exog_cols + instr_cols
		ols_cols.append('const')
		summ_ols = reg_ols.summary(yname=endog_cols[0], xname=ols_cols)
		output += getOLSOutputTable(summ_ols)
		output += copyButton()
		
		return output
		
def getOLSOutputTable(summary):
	main_table = summary.tables[1].data
		
	additional_info = summary.tables[0].data
	r2 = float(additional_info[0][-1].strip())
	nobs = int(additional_info[5][1].strip())
	dep_var = additional_info[0][1]
	
	heads = main_table[0]
	heads[0] = dep_var
	df_data = pd.DataFrame(main_table[1:], columns=heads)
	df_data = df_data.iloc[:, [0,1,2,4]]
	df_data = df_data.T
	
	cols = df_data.columns.tolist()
	cols = cols[-1:] + cols[:-1]
	df = df_data[cols]
		
	out = '<table class="table table-striped">' + '\n'
	for i, row in df.iterrows():
		if i == 0:
			out += '    <thead>' + '\n'
			out += '        <tr>' + '\n'
			out += '            <th scope"col" class="font-weight-normal">' + str(i) + '</th>' + '\n'
			for col in cols:
				out += '            <th scope"col" class="font-weight-normal">' + str(row[col]) + '</th>' + '\n'
			out += '        </tr>' + '\n'
			out += '    </thead>' + '\n'
			out += '    <tbody>' + '\n'
		else:
			out += '        <tr>' + '\n'
			out += '            <th scope"col" class="font-weight-normal">' + str(i) + '</th>' + '\n'
			for col in cols:
				out += '            <th scope"col" class="font-weight-normal">' + str(row[col]) + '</th>' + '\n'
			out += '        </tr>' + '\n'
	out += '        <tr>' + '\n'
	out += '            <th scope"col" class="font-weight-normal">r-squared</th>' + '\n'
	out += '            <th scope"col" class="font-weight-normal">' + str(r2) + '</th>' + '\n'
	for j in range(len(cols)-1):	
		out += '            <th scope"col" class="font-weight-normal"></th>' + '\n'
	out += '        </tr>' + '\n'
	out += '        <tr>' + '\n'
	out += '            <th scope"col" class="font-weight-normal">no. observations</th>' + '\n'
	out += '            <th scope"col" class="font-weight-normal">' + str(nobs) + '</th>' + '\n'
	for j in range(len(cols)-1):
		out += '            <th scope"col"></th>' + '\n'
	out += '        </tr>' + '\n'
	out += '    </tbody>' + '\n'
	out += '</table>' + '\n'
	#print(out)
		
	return 'OLS Regression Results\n' + out
	
def get2SLSOutputTable(summary):
	main_table = summary.tables[1].data
	additional_info = summary.tables[0].data

	r2 = float(additional_info[0][-1].strip())
	nobs = int(additional_info[6][1].strip())
	dep_var = additional_info[0][1]
	
	heads = main_table[0]
	heads[0] = dep_var
	df_data = pd.DataFrame(main_table[1:], columns=heads)
	df_data = df_data.iloc[:, [0,1,2,4]]
	df_data = df_data.T
	
	cols = df_data.columns.tolist()
	cols = cols[-1:] + cols[:-1]
	df = df_data[cols]
		
	out = '<table class="table table-striped">' + '\n'
	for i, row in df.iterrows():
		if i == 0:
			out += '    <thead>' + '\n'
			out += '        <tr>' + '\n'
			out += '            <th scope"col" class="font-weight-normal">' + str(i) + '</th>' + '\n'
			for col in cols:
				out += '            <th scope"col" class="font-weight-normal">' + str(row[col]) + '</th>' + '\n'
			out += '        </tr>' + '\n'
			out += '    </thead>' + '\n'
			out += '    <tbody>' + '\n'
		else:
			out += '        <tr>' + '\n'
			out += '            <th scope"col" class="font-weight-normal">' + str(i) + '</th>' + '\n'
			for col in cols:
				out += '            <th scope"col" class="font-weight-normal">' + str(row[col]) + '</th>' + '\n'
			out += '        </tr>' + '\n'
	out += '        <tr>' + '\n'
	out += '            <th scope"col" class="font-weight-normal">r-squared</th>' + '\n'
	out += '            <th scope"col" class="font-weight-normal">' + str(r2) + '</th>' + '\n'
	for j in range(len(cols)-1):
		out += '            <th scope"col"></th>' + '\n'
	out += '        </tr>' + '\n'
	out += '        <tr>' + '\n'
	out += '            <th scope"col" class="font-weight-normal">no. observations</th>' + '\n'
	out += '            <th scope"col" class="font-weight-normal">' + str(nobs) + '</th>' + '\n'
	for j in range(len(cols)-1):
		out += '            <th scope"col"></th>' + '\n'
	out += '        </tr>' + '\n'
	out += '    </tbody>' + '\n'
	out += '</table>' + '\n'
	#print(out)
		
	return '2SLS Regression Results\n' + out
	
def copyButton():
	out = '\n<button class="btn btn-secondary" id="copy">Copy Output</button>'
	return out