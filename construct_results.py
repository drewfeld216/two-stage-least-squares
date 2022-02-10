import os
import pandas as pd
from statsmodels.sandbox.regression.gmm import IV2SLS
import statsmodels.api as sm
import numpy as np


def getColsAsIterable(filename):
	df_file = pd.read_csv(filename)
	cols = list(df_file.columns)
	count = list(range(len(cols)))
	out = [(col, i) for col, i in zip(cols, count)]
	return out

def runRegression(filepath, data_dict):
	data = pd.read_csv(filepath)
	data_cols = list(data.columns)
		
	endog_cols = [ col for col in data_cols if col in data_dict['endog'] ]	
	exog_cols = [ col for col in data_cols if col in data_dict['exog'] ]
	instr_cols = [ col for col in data_cols if col in data_dict['instr'] ]
		
	if len(endog_cols) > 1:
		raise IndexError
		
	if (len(instr_cols) != len(exog_cols)) and len(instr_cols) > 0:
		raise ValueError
		
	endog = data[endog_cols].to_numpy()
	exog = data[exog_cols].to_numpy()
	instr = data[instr_cols].to_numpy()
		
	const = np.ones(endog.shape)
	
	exog = np.concatenate([exog, const], axis=1)
	instr = np.concatenate([instr, const], axis=1)

	if len(instr_cols) == 0:
		mod = sm.OLS(endog, exog)
		reg = mod.fit()
		exog_cols.append('const')
		summ = reg.summary(yname=endog_cols[0], xname=exog_cols)
		output = getOLSOutputTable(summ)
		return output
	
	else:
		mod_2sls = IV2SLS(endog, exog, instr)
		reg_2sls = mod_2sls.fit()
		exog_cols.append('const')
		summ_2sls = reg_2sls.summary(yname=endog_cols[0], xname=exog_cols)
		output = get2SLSOutputTable(summ_2sls)
		
		exog_only_cols = [col for col in exog_cols if col not in instr_cols and col != 'const']
		instr_only_cols = [col for col in instr_cols if col not in exog_cols and col != 'const']

		exog_only = data[exog_only_cols].to_numpy()
		instr_only = data[instr_only_cols].to_numpy()
				
		instr_only = np.concatenate([instr_only, np.ones(instr_only.shape)], axis=1)
		
		mod_ols = sm.OLS(exog_only, instr_only)
		print(mod_ols)
		reg_ols = mod_ols.fit()
		print(reg_ols)
		instr_only_cols.append('const')
		print(instr_only_cols)
		summ_ols = reg_ols.summary(yname=exog_only_cols[0], xname=instr_only_cols)
		print(summ_ols)
		output += getOLSOutputTable(summ_ols)
		
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
			out += '            <th scope"col">' + str(i) + '</th>' + '\n'
			for col in cols:
				out += '            <th scope"col">' + str(row[col]) + '</th>' + '\n'
			out += '        </tr>' + '\n'
			out += '    </thead>' + '\n'
			out += '    <tbody>' + '\n'
		else:
			out += '        <tr>' + '\n'
			out += '            <th scope"col">' + str(i) + '</th>' + '\n'
			for col in cols:
				out += '            <th scope"col">' + str(row[col]) + '</th>' + '\n'
			out += '        </tr>' + '\n'
	out += '        <tr>' + '\n'
	out += '            <th scope"col">r-squared</th>' + '\n'
	out += '            <th scope"col">' + str(r2) + '</th>' + '\n'
	for j in range(len(cols)-1):	
		out += '            <th scope"col"></th>' + '\n'
	out += '        </tr>' + '\n'
	out += '        <tr>' + '\n'
	out += '            <th scope"col">no. observations</th>' + '\n'
	out += '            <th scope"col">' + str(nobs) + '</th>' + '\n'
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
			out += '            <th scope"col">' + str(i) + '</th>' + '\n'
			for col in cols:
				out += '            <th scope"col">' + str(row[col]) + '</th>' + '\n'
			out += '        </tr>' + '\n'
			out += '    </thead>' + '\n'
			out += '    <tbody>' + '\n'
		else:
			out += '        <tr>' + '\n'
			out += '            <th scope"col">' + str(i) + '</th>' + '\n'
			for col in cols:
				out += '            <th scope"col">' + str(row[col]) + '</th>' + '\n'
			out += '        </tr>' + '\n'
	out += '        <tr>' + '\n'
	out += '            <th scope"col">r-squared</th>' + '\n'
	out += '            <th scope"col">' + str(r2) + '</th>' + '\n'
	for j in range(len(cols)-1):
		out += '            <th scope"col"></th>' + '\n'
	out += '        </tr>' + '\n'
	out += '        <tr>' + '\n'
	out += '            <th scope"col">no. observations</th>' + '\n'
	out += '            <th scope"col">' + str(nobs) + '</th>' + '\n'
	for j in range(len(cols)-1):
		out += '            <th scope"col"></th>' + '\n'
	out += '        </tr>' + '\n'
	out += '    </tbody>' + '\n'
	out += '</table>' + '\n'
	#print(out)
		
	return '2SLS Regression Results\n' + out