import os
from flask import Flask, render_template, request, send_file
from datetime import datetime
from main import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            #filename = secure_filename(file.filename)
            time_stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
            filename = f"{time_stamp}.{file.filename.split('.')[-1]}"
            file.save(os.path.join('uploads', filename))
            
            meta_model, middle_model = LoadModel(model_type="ResNet")
            result_file = image2midi(image_path=os.path.join('uploads', filename), 
                                     index=filename.split('.')[0],  meta_model=meta_model, 
                                     middle_model=middle_model)
            return send_file(result_file, as_attachment=True, attachment_filename="result.mid")
 

if __name__ == "__main__":
    print("Visit http://localhost:5000/ to upload your image.")
    app.run(debug=True)