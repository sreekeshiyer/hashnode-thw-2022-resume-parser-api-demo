import boto3
from textract import process
from os.path import join as ojoin
from os import remove as ormv
from os import getenv
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from spacy import load as load_spacy_model
from spacy.cli import download as download_spacy_model
from spacy.matcher import Matcher
from re import findall
from config import boto_config
from json import dumps
from time import time

SAVE_DIR = "./static/temp/"
ALLOWED_EXTENSIONS = {"txt", "pdf", "doc", "docx"}

def allowed_file(filename: str) -> bool:
    """
    Utility function to check whether a file has a valid extension. 
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(file: FileStorage) -> dict[str, str]:
    """
    Extracts text from a file using the textract module.
    """
    if file and allowed_file(file.filename):

        # Create a secure version of the filename
        filename = secure_filename(file.filename)

        # Save the file locally
        file.save(ojoin(SAVE_DIR, filename))
        currFile = ojoin(SAVE_DIR) + filename

        # Extract text
        text = str(process(currFile).decode("utf-8"))
        
        # Remove the file from the file system
        ormv(ojoin(SAVE_DIR, filename))

        return {"text": text, "filename": filename}


def extract_name_and_email(text: str) -> dict[str, str]:
    """
        Extract name and email from Resume file. \n
        Returns a dictionary.
    """

    # Load pre-trained model
    try:
        nlp = load_spacy_model("en_core_web_sm")
    except:  # If not present, we download
        download_spacy_model("en_core_web_sm")
        nlp = load_spacy_model("en_core_web_sm")

    # Initialize Matcher with a Vocabulary

    matcher = Matcher(nlp.vocab)

    def extract_name(text: str) -> str:
        """
        Extract name from resume text using NLP
        """
        nlp_text = nlp(text)

        # First name and Last name are always Proper Nouns
        pattern = [{"POS": "PROPN"}, {"POS": "PROPN"}]
        matcher.add("NAME", [pattern])

        matches = matcher(nlp_text)

        for match_id, start, end in matches:
            span = nlp_text[start:end]
            return span.text

    def extract_email(text: str) -> str:
        """
        Extract email using Regular Expression
        """
        email = findall("([^@|\s]+@[^@]+\.[^@|\s]+)", text)
        if email:
            try:
                return email[0].split()[0].strip(";")
            except IndexError:
                return None

    return {
        "email": extract_email(text),
        "name": extract_name(text)
    }


def upload_file_to_bucket(obj: dict[str, str], filename: str) -> None:

    #! You can refer to this, to check if the right emails are extracted
    print(obj)
    
    # Create an S3 Resource
    s3 = boto3.resource(
        's3', 
        config=boto_config, 
        aws_access_key_id=getenv('ACCESS_KEY'), 
        aws_secret_access_key=getenv('SECRET_KEY'))
    new_file = filename.split('.')[0]
    
    # Put the JSON object to the bucket
    s3.Bucket('YOUR_BUCKET_NAME').put_object(
        Body=dumps(obj),
        Key=f'{new_file}_{int(time())}.json',
        ContentType='application/json'
    )
