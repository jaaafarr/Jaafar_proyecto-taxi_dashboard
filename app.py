from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    # Load dataset
    df = pd.read_csv('nyc_taxi.csv')
    summary = df.describe(include='all').to_html(classes='table table-striped')
    head = df.head().to_html(classes='table table-bordered')
    return render_template('index.html', summary=summary, head=head)

if __name__ == '__main__':
    app.run(debug=True)
