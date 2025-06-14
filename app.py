from flask import *
# Creating the Flask application instance
app = Flask(__name__)
from flask_cors import CORS
CORS(app)

# Mpesa Payment Route
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

# setting up file upload
import os
app.config['UPLOAD_FOLDER'] = 'static/images'
import pymysql
import pymysql.cursors


@app.route('/api/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']

    connection = pymysql.connect(
        host='CharlesDavid123.mysql.pythonanywhere-services.com',
        user='',
        password='',
        database='CharlesDavid123$ecommerce'
    )
    cursor = connection.cursor()
    sql = 'INSERT INTO users(username,email,password, phone) VALUES (%s,%s,%s,%s)'
    data = (username, email, password, phone)
    cursor.execute(sql, data)
    connection.commit()
    return jsonify({"success": "Thank you for Joining"})

@app.route('/api/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']
    connection = pymysql.connect(
        host='CharlesDavid123.mysql.pythonanywhere-services.com',
        user='',
        password='',
        database='CharlesDavid123$ecommerce'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM users WHERE email = %s AND password = %s"
    cursor.execute(sql, (email, password))
    user = cursor.fetchone()
    if not user:
        return jsonify({"message": "Login Failed"})
    return jsonify({"message": "Login success", "user": user})

@app.route('/api/admin_signup', methods=['POST'])
def admin_signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']

    connection = pymysql.connect(
        host='CharlesDavid123.mysql.pythonanywhere-services.com',
        user='',
        password='',
        database='CharlesDavid123$ecommerce'
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({"error": "Admin already exists with this email"}), 409

    sql = 'INSERT INTO admins (username, email, password, phone) VALUES (%s, %s, %s, %s)'
    data = (username, email, password, phone)
    cursor.execute(sql, data)
    connection.commit()
    return jsonify({"success": "Admin registered successfully"}), 201


@app.route('/api/admin_login', methods=['POST'])
def admin_login():
    email = request.form['email']
    password = request.form['password']

    connection = pymysql.connect(
        host='CharlesDavid123.mysql.pythonanywhere-services.com',
        user='',
        password='',
        database='CharlesDavid123$ecommerce'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM admins WHERE email = %s AND password = %s"
    cursor.execute(sql, (email, password))
    admin = cursor.fetchone()
    if not admin:
        return jsonify({"message": "Invalid admin credentials"}), 401
    return jsonify({"message": "Admin login successful", "admin": admin}), 200

@app.route('/api/add_product', methods=['POST'])
def add_product():
    product_name = request.form['product_name']
    product_description = request.form['product_description']
    product_cost = request.form['product_cost']
    photo = request.files['product_photo']
    filename = photo.filename
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    photo.save(photo_path)
    connection = pymysql.connect(
        host='CharlesDavid123.mysql.pythonanywhere-services.com',
        user='',
        password='',
        database='CharlesDavid123$ecommerce'
    )
    cursor = connection.cursor()
    sql = 'INSERT INTO product_details (product_name, product_description, product_cost, product_photo) VALUES (%s, %s, %s, %s)'
    data = (product_name, product_description, product_cost, filename)
    cursor.execute(sql, data)
    connection.commit()
    return jsonify({"success": "Product details added successfully"})

@app.route('/api/get_product_details', methods=['GET'])
def get_product_details():
    connection = pymysql.connect(
        host='CharlesDavid123.mysql.pythonanywhere-services.com',
        user='',
        password='',
        database='CharlesDavid123$ecommerce'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM product_details')
    product_details = cursor.fetchall()
    return jsonify(product_details)


@app.route('/api/update_product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product_name = request.form['product_name']
    product_description = request.form['product_description']
    product_cost = request.form['product_cost']
    product_photo = request.files.get('product_photo', None)

    connection = pymysql.connect(
        host='CharlesDavid123.mysql.pythonanywhere-services.com',
        user='',
        password='',
        database='CharlesDavid123$ecommerce'
    )
    cursor = connection.cursor()

    if product_photo:
        filename = product_photo.filename
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        product_photo.save(photo_path)
        sql = '''UPDATE product_details
                 SET product_name=%s, product_description=%s, product_cost=%s, product_photo=%s
                 WHERE product_id=%s'''
        data = (product_name, product_description, product_cost, filename, product_id)
    else:
        sql = '''UPDATE product_details
                 SET product_name=%s, product_description=%s, product_cost=%s
                 WHERE product_id=%s'''
        data = (product_name, product_description, product_cost, product_id)

    cursor.execute(sql, data)
    connection.commit()
    return jsonify({"success": "Product updated successfully"}), 200

@app.route('/api/delete_product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    connection = pymysql.connect(
        host='CharlesDavid123.mysql.pythonanywhere-services.com',
        user='',
        password='',
        database='CharlesDavid123$ecommerce'
    )
    cursor = connection.cursor()
    cursor.execute("DELETE FROM product_details WHERE product_id = %s", (product_id,))
    connection.commit()
    return jsonify({"success": "Product deleted successfully"}), 200

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    amount = request.form['amount']
    phone = request.form['phone']
    consumer_key = "i1YLkSnp0jEAOqtCQ7SIbp6gxio3vVt9QsgvGgfI98xSHAvN"
    consumer_secret = "fCuvojmfvNv04nlnpa4JJ8MwtaSDgMBMFVdoD2kDACKTJzvwuF2w77eJzrxA9NaE"
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = response.json()
    access_token = "Bearer " + data['access_token']
    timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    business_short_code = "174379"
    data_to_encode = business_short_code + passkey + timestamp
    encoded = base64.b64encode(data_to_encode.encode())
    password = encoded.decode()
    payload = {
        "BusinessShortCode": "174379",
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": "174379",
        "PhoneNumber": phone,
        "CallBackURL": "https://coding.co.ke/api/confirm.php",
        "AccountReference": "charles shop",
        "TransactionDesc": "Payments for Products"
    }
    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json"
    }
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})



if __name__ == '__main__':
    app.run(debug=True)
