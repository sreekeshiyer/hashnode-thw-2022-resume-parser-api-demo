from flask import Flask, render_template, request
from utils import extract_text_from_file, extract_name_and_email, upload_file_to_bucket

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_files_to_bucket', methods=["POST"])
def add_files_to_bucket():
    mail_count = 0
    for file in request.files.getlist("resume"):
        if file.filename != "":

            extracted_response = extract_text_from_file(file)

            filename = extracted_response['filename']
            text = extracted_response['text']

            obj = extract_name_and_email(text)
            upload_file_to_bucket(obj=obj, filename=filename)

            mail_count += 1

    return render_template('success.html', no_of_mails=mail_count)


if __name__ == '__main__':
    app.run(debug=True)