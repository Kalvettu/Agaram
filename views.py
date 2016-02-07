import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from time import time
from datetime import datetime
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, jsonify
from werkzeug import secure_filename


TEMP_FOLDER = 'static/temporary/'
UPLOAD_FOLDER = 'static/uploads/'
SEGMENTED_INSCRIPTIONS = 'static/segmented/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/', methods = ['GET', 'POST'])
def index():
	return render_template('index.html')

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():

	if request.method == 'POST':

		file = request.files['file']
		response = {}

		if file and allowed_file(file.filename):
			print 'im of'
			now = datetime.now()
			filename = now.strftime('%Y-%m-%d-%H-%M-%S') + '_' + secure_filename(file.filename) 
			file.save(os.path.join(UPLOAD_FOLDER, filename))
			response['first_save'] = url_for('uploaded_file', filename=filename)
			#load image
			dir = os.curdir
			img = filename
			print img
			path = os.path.join(UPLOAD_FOLDER,img)
			raw_image = cv2.imread(path,0)
			
			#blur image to remove noise
			#sm_image = cv2.medianBlur(raw_image, 3)
			threshold = int(request.form['threshold'])
			sm_image = cv2.bilateralFilter(raw_image, 25, 50, 50)
			ret,bw_image = cv2.threshold(sm_image,threshold,255,cv2.THRESH_BINARY_INV)
			print 'check'
			cv2.imwrite(os.path.join(TEMP_FOLDER, filename), bw_image)
			return jsonify({
				'url': 'static/temporary/'+filename,
				'error': 0,
				'threshold': threshold
			})

	else:
		return jsonify({'error': 1})

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5000)