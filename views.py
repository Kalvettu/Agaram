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

		if file and allowed_file(file.filename):

			now = datetime.now()
			filename = now.strftime('%Y-%m-%d-%H-%M-%S') + '_' + secure_filename(file.filename) 
			file.save(os.path.join(UPLOAD_FOLDER, filename))
			
			#load image
			dir = os.curdir
			img = filename
			path = os.path.join(UPLOAD_FOLDER,img)
			raw_image = cv2.imread(path,0)
			
			#blur image to remove noise
			#sm_image = cv2.medianBlur(raw_image, 3)
			threshold = int(request.form['threshold'])
			sm_image = cv2.bilateralFilter(raw_image, 25, 50, 50)
			ret,bw_image = cv2.threshold(sm_image,threshold,255,cv2.THRESH_BINARY_INV)
			cv2.imwrite(os.path.join(TEMP_FOLDER, filename), bw_image)
			
			return jsonify({
				'original': url_for('uploaded_file', filename=filename),
				'error': 0,
				'threshold': threshold,
				'url': 'static/temporary/'+filename,
			})

	else:
		return jsonify({'error': 1})

@app.route('/generate', methods = ['GET', 'POST'])
def generate_file():

	if request.method == 'POST':
		bw_image = cv2.imread(request.json['url'],0)
		kernel = np.ones((1.5,1.5),np.uint8)
		er_image = cv2.erode(bw_image,kernel)
		kernel = np.ones((2,2),np.uint8)
		di_image = cv2.dilate(er_image,kernel, iterations=1)

		#find contours
		mo_image = di_image.copy()
		contour0 = cv2.findContours(mo_image.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
		contours = [cv2.approxPolyDP(cnt,3,True) for cnt in contour0[0]]

		maxArea = 0
		rect=[]

		for ctr in contours:
		    maxArea = max(maxArea,cv2.contourArea(ctr))

		areaRatio = 0.05

		for ctr in contours:    
		    if cv2.contourArea(ctr) > maxArea * areaRatio: 
		        rect.append(cv2.boundingRect(cv2.approxPolyDP(ctr,1,True)))

		symbols=[]
		for i in rect:
		    x = i[0]
		    y = i[1]
		    w = i[2]
		    h = i[3]
		    p1 = (x,y)
		    p2 = (x+w,y+h)
		    cv2.rectangle(mo_image,p1,p2,255,2)
		    image = cv2.resize(mo_image[y:y+h,x:x+w],(32,32))
		    symbols.append(image.reshape(1024,).astype("uint8"))

		#segment images and export them
		testset_data = np.array(symbols)
		#plt.show()
		# show glyphs
		img_name_base = str(time()) + '_'
		for i in range(len(symbols)):
			image = np.zeros(shape=(64,64))
			image[15:47,15:47] = symbols[i].reshape((32,32))
			segment_name = img_name_base + str(i) + '.jpg'
			cv2.imwrite(os.path.join(SEGMENTED_INSCRIPTIONS, segment_name), image)
		return jsonify({'error': 'asd'})

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5000)