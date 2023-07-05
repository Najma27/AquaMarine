from flask import Flask, render_template, request, send_from_directory, url_for, session
from cryptography.fernet import Fernet
import os

main = Flask(__name__)
main.config['UPLOAD_FOLDER'] = 'uploads'
main.config['SECRET_KEY'] = os.urandom(24)

def generate_key():
    return Fernet.generate_key()

def encrypt_file(filename, key):
    fernet = Fernet(key)
    with open(os.path.join(main.config['UPLOAD_FOLDER'], filename), 'rb') as file:
        data = file.read()
    encrypted_data = fernet.encrypt(data)
    encrypted_filename = f'{os.path.splitext(filename)[0]}_encrypted.xml'
    with open(os.path.join(main.config['UPLOAD_FOLDER'], encrypted_filename), 'wb') as file:
        file.write(encrypted_data)
    return encrypted_filename

def decrypt_file(filename, key):
    fernet = Fernet(key)
    with open(os.path.join(main.config['UPLOAD_FOLDER'], filename), 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    decrypted_filename = f'{os.path.splitext(filename)[0]}_decrypted.xml'
    with open(os.path.join(main.config['UPLOAD_FOLDER'], decrypted_filename), 'wb') as file:
        file.write(decrypted_data)
    return decrypted_filename

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = file.filename
    file_path = os.path.join(main.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Validate file format (check if it is an XML file)
    if not filename.endswith('.xml'):
        return render_template('index.html', message='Invalid file format. Only XML files are allowed.'  )

    key = generate_key()
    session['encryption_key'] = key.decode()  # Save encrypt file for uploader
    encrypted_filename = encrypt_file(filename, key)
    encrypted_file_link = url_for('download', filename=encrypted_filename)
    return render_template('index.html', message='File uploaded and encrypted successfully!', encrypted_file_link=encrypted_file_link)

@main.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    return send_from_directory(main.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@main.route('/decrypt', methods=['POST'])
def decrypt():
    filename = request.form['filename']
    decryption_key = request.form['decryption_key']

    decrypted_filename = decrypt_file(filename, decryption_key.encode())
    decrypted_file_link = url_for('download', filename=decrypted_filename)
    return render_template('index.html', message='File decrypted successfully!', decrypted_file_link=decrypted_file_link)

if __name__ == '__main__':
    main.run(host='0.0.0.0', port=5000, debug=True)