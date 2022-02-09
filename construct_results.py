import os
import pandas as pd
from statsmodels.sandbox.regression.gmm import IV2SLS
import numpy as np

def getColsAsIterable(filename):
	df_file = pd.read_csv(filename)
	cols = list(df_file.columns)
	count = list(range(len(cols)))
	out = [(col, i) for col, i in zip(cols, count)]
	return out
	
def regressionHTML(endog, exog, instr):
	results = runRegression(endog, exog, instr)
	#formatting
	return

def runRegression(filepath, data_dict):
	data = pd.read_csv(filepath)
	data_cols = list(data.columns)
	
	endog_cols = [ col for col in data_cols if col in data_dict['endog'] ]	
	exog_cols = [ col for col in data_cols if col in data_dict['exog'] ]
	instr_cols = [ col for col in data_cols if col in data_dict['instr'] ]
	
	if len(endog_cols) > 1:
		raise IndexError
		
	if len(instr_cols) != len(exog_cols):
		raise ValueError
		
	endog = data[endog_cols].to_numpy()
	exog = data[exog_cols].to_numpy()
	instr = data[instr_cols].to_numpy()
	
	mod = IV2SLS(endog, exog, instr)
	reg = mod.fit()
	summ = reg.summary(yname=endog_cols[0], xname=instr_cols)
	output = summ.tables[0].as_html() + summ.tables[1].as_html() + summ.tables[2].as_html()
	return output