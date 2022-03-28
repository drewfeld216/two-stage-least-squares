# two-stage-least-squares

A web-based tool for fitting two-stage least-squares, originally designed for use in Columbia Business School's _The Analytics Advantage_ course.

https://two-stage-least-squares.herokuapp.com/

How to use:
1. Upload data file (.csv and .xlsx accepted)
2. Categorize columns/variables as either dependent, exogenous explanatory, endogenous explanatory, or instrumental
3. Run regression

If no instrumental variables are given, OLS will be performed using _all_ explanatory variables (exog and endog).
