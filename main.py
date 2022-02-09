import os

from flask import Flask, flash, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import construct_results


# create and configure the app
app = Flask(__name__, instance_relative_config=True)

app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
)


app.config['UPLOAD_FOLDER'] = './app/static/uploads'

if test_config is None:
    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)
else:
    # load the test config if passed in
    app.config.from_mapping(test_config)

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
    if request.method == 'POST':
        data = request.get_data().decode('utf-8')
        data = data.split('&')
        data = [section.split("=") for section in data]
        data_dict = {bit[0]:bit[1] for bit in data}
                    
        try:
            results = construct_results.runRegression(app.config['UPLOAD_LOCATION'], data_dict)
        except:
            return "<p>Not able to fit regression model. Please check data and try again.</p>"
        
    return results
        
  
if __name__ == "__main__":
    app.run()