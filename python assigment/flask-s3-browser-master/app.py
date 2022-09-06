from flask import Flask, render_template, request, redirect, url_for, flash, \
    Response, session
from flask_bootstrap import Bootstrap
import boto3
from filters import datetimeformat, file_type
from resources import get_bucket, get_buckets_list, show_bucket 

app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'secret'
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bucket = request.form['bucket']
        session['bucket'] = bucket
        return redirect(url_for('files'))
    else:
        buckets = get_buckets_list()
        return render_template("index.html", buckets=buckets)


@app.route('/files')
def files():
    buckets=get_buckets_list()
    my_bucket = get_bucket()
    summaries = my_bucket.objects.all()

    return render_template('files.html', my_bucket=my_bucket, files=summaries, buckets=buckets)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    my_bucket = get_bucket()
    my_bucket.Object(file.filename).put(Body=file)

    flash('File uploaded successfully')
    return redirect(url_for('files'))


@app.route('/delete', methods=['POST'])
def delete():
    key = request.form['key']

    my_bucket = get_bucket()
    my_bucket.Object(key).delete()

    flash('File deleted successfully')
    return redirect(url_for('files'))


@app.route('/download', methods=['POST'])
def download():
    key = request.form['key']

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )

@app.route('/create', methods=['POST'])
def create():
    new_bucket=request.form['new_bucket']
    s3 = boto3.client('s3')
    s3.create_bucket(Bucket=new_bucket)

    flash('New bucket created successfully')
    return redirect(url_for('index'))

@app.route('/copy', methods=['POST'])
def copy():
    cbucket = request.form['cbucket']
    cfile = request.form['cfile']
    tbucket = request.form['tbucket']
    s3 = boto3.resource('s3')
    copy_source = {
     'Bucket': cbucket,
     'Key': cfile}
    bucket = s3.Bucket(tbucket)
    bucket.copy(copy_source, cfile)
    flash('File copied sucessfully')
    return redirect(url_for('files'))

if __name__ == "__main__":
    app.run()

