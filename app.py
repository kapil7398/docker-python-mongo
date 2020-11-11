from flask import Flask, render_template, request, url_for,send_from_directory,redirect
from flask_pymongo import PyMongo
import os

#importing pillow for image handling
from PIL import Image
from PIL.ExifTags import TAGS


from PIL import ExifTags
import binascii
from PIL.TiffImagePlugin import IFDRational

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=1, username='guest', password='guest'))
users.append(User(id=2, username='root', password='root'))
users.append(User(id=3, username='admin', password='admin'))


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://mongo:27017/docker-flask-mongo'
mongo = PyMongo(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            return render_template('upload.html')

        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/upload', methods=['POST'])
def image_upload():
    target = os.path.join(APP_ROOT, 'images/')  #folder path
    if not os.path.isdir(target):
        os.mkdir(target)     # create folder if not exits

    
    for image in request.files.getlist("image"): 
        filename = image.filename
        destination = "/".join([target, filename])
        image.save(destination)

    my_img = Image.open(destination)
    exifdata = my_img.getexif()

    metadict={}
    metadict['image'] = filename
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        if tag == 'MakerNote':
            continue
        data = exifdata.get(tag_id)
        # decode bytes 
        if isinstance(data, IFDRational):
            data = str('NA')
        if isinstance(data, bytes):
            hex_data = binascii.hexlify(data)
            data = hex_data.decode('utf-8')
    
        metadict[tag] = str(data)

        
    mongo.db.metadata.insert(metadict) 

    return 'Image Uploaded Successfully!!!'


@app.route('/search' ,methods=['GET','POST'])

def search_image():
    return render_template('search.html')



@app.route('/gallery/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

@app.route('/gallery', methods=['GET','POST'])
def get_gallery():
    
    key1 = request.form.get("key1")
    key2 = request.form.get("key2")
    key3 = request.form.get("key3")
    key4 = request.form.get("key4")
    value1 = request.form.get("value1")
    value2 = request.form.get("value2")
    value3 = request.form.get("value3")
    value4 = request.form.get("value4")
    key_value_pairs={}
    
    if(key1 != "" and value1 != ""):
        key_value_pairs[key1] = value1
    
    if(key2 != "" and value2 != ""):
        key_value_pairs[key2] = value2
    
    if(key3 != "" and value3 != ""):
        key_value_pairs[key3] = value3
    
    if(key4 != "" and value4 != ""):
        key_value_pairs[key4] = value4

    results = list(mongo.db.metadata.find(key_value_pairs))
    image_names = []
    for i in results:
        print(i)
        print('\n\n')
        image_names.append(i['image'])
    

    
    return render_template("gallery.html", image_names=image_names)

    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 80,debug=True)