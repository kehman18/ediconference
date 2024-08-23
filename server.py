import csv
import os
import uuid
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image

app = Flask(__name__)

# Define the path to save uploaded images
UPLOAD_FOLDER = './static/uploaded_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def my_home():
    return render_template('index.html')

@app.route("/<string:page_name>")
def html_page(page_name):
    if not page_name.endswith(".html"):
        page_name += ".html"
    return render_template(page_name)

# Function to center and merge two images
def center_image(image_1_path, image_2_path, output_path):
    with Image.open(image_1_path) as img1, Image.open(image_2_path) as img2:
        img2 = img2.resize((250, 250))

        if img2.mode != 'RGBA':
            img2 = img2.convert('RGBA')
        width1, height1 = img1.size
        center_x = width1 // 2
        center_y = height1 // 2

        paste_x = center_x - 125
        paste_y = center_y - 125

        composite = Image.new('RGBA', img1.size)
        composite.paste(img1, (0, 0))
        composite.paste(img2, (paste_x, paste_y), img2)

        if img1.mode != 'RGBA':
            composite = composite.convert('RGB')

        composite.save(output_path)

# Function to write user data to file
def write_to_file(data):
    with open('database.txt', mode='a') as database:
        first_name = data["first name"]
        last_name = data['last name']
        sex = data['sex']
        email = data['email']
        phone_number = data['phone number']
        location = data['Location']
        expectations = data['message']
        database.write(f'\n{first_name}, {last_name}, {sex}, {email}, {phone_number}, {location}, {expectations}')

# Function to write user data to CSV
def write_to_csv(data):
    with open('database.csv', mode='a', newline='') as database2:
        first_name = data["first name"]
        last_name = data['last name']
        sex = data['sex']
        email = data['email']
        phone_number = data['phone number']
        location = data['Location']
        expectations = data['message']
        csv_writer = csv.writer(database2, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([first_name, last_name, sex, email, phone_number, location, expectations])

# Route to handle form submission
@app.route('/submit_form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        data = request.form.to_dict()
        write_to_csv(data)

        merged_image_filename = None
        if 'image_upload' in request.files:
            image_upload = request.files['image_upload']
            if image_upload.filename != '':
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                
                uploaded_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_upload.filename)
                image_upload.save(uploaded_image_path)
                
                image_1_path = './static/EC_templates.png'
                merged_image_filename = f'merged_{uuid.uuid4()}.png'
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], merged_image_filename)

                center_image(image_1_path, uploaded_image_path, output_path)

        return redirect(url_for('thankyou_index', merged_image=merged_image_filename))
    else:
        return "Oops, something went wrong. Please try again."

@app.route('/thankyou_index')
def thankyou_index():
    merged_image = request.args.get('merged_image', None)
    return render_template('thankyou_index.html', merged_image=merged_image)

if __name__ == "__main__":
    app.run(debug=True)
