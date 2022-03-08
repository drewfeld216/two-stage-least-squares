import os
import sys

from flask import Flask, flash, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import construct_results
import urllib.parse as prs

# create and configure the app
app = Flask(__name__, instance_relative_config=True)

app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
)


app.config['UPLOAD_FOLDER'] = './static/uploads'

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass   

    
@app.route('/', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files: 
            flash('No file part')
            return render_template('home.html')
    
        file = request.files['file']
                    
        if file.filename == '':
            flash('No selected file')
            return render_template('home.html')
        
        if file:
            filename = secure_filename(file.filename)
            g_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(g_filepath)
            cols = construct_results.getColsAsIterable(g_filepath)
            app.config['UPLOAD_LOCATION'] = g_filepath
            return render_template('results.html', filename=filename, columns=cols)
    
    return render_template('home.html')
    
@app.route('/get-regression', methods=['POST', 'GET'])
def get_regression():
    print(app.config['UPLOAD_LOCATION'], file=std.stderr)
    if request.method == 'POST':
        data = prs.unquote_plus(request.get_data().decode('utf-8'))
        data = data.split('&')
        data = [section.split("=") for section in data]
        data_dict = {'dep': [], 'endog': [], 'exog': [], 'instr': []}
        for bit in data:
            data_dict[bit[0][:-2]].append(int(bit[1]))
                                
        try:
            results = construct_results.runRegression(app.config['UPLOAD_LOCATION'], data_dict)
        except IndexError:
            return "<p>You have selected too many outcome variables.</p>"
        except Exception as e:
            print(e, file = sys.stderr)
            return "<p>Not able to fit regression model. Please check data and try again.</p>"
        
    return results
        
  
if __name__ == "__main__":
    app.run()