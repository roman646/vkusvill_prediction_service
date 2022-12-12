import os
import logging
from flask import Flask, render_template, request, redirect

from utils import is_allowed_file, ProfitabilityModels

app = Flask(__name__)

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
INPUT_FILE_NAME = 'sales_data.xlsx'
OUTPUT_FILE_NAME = 'static/profitability_prediction.xlsx'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result')
def download_result():
    return render_template('result.html')


@app.route('/upload_file', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        names = os.listdir()
        for i in names:
            if os.path.isfile(i) and i == OUTPUT_FILE_NAME:
                os.remove(i)

        file = request.files["file"]

        logging.error(f'loading file {file.filename}')

        if is_allowed_file(file.filename):
            file.save(INPUT_FILE_NAME)
            try:
                model = ProfitabilityModels(INPUT_FILE_NAME)
                result = model.make_predictions()
                logging.info(result)
                result.to_excel(OUTPUT_FILE_NAME)
            except Exception as e:
                logging.error('Some error with prediction')
                logging.error(str(e))

        return redirect('/result')

    return render_template("loading.html")


if __name__ == '__main__':
    PORT = os.getenv('PORT', 1234)
    app.run(host='0.0.0.0', port=PORT)
