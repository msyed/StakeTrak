#to delete files
import os, shutil

#web application framework written in python
from flask import Flask, request, url_for, make_response, redirect, render_template

#to restrict types of files
from werkzeug import secure_filename

#personal python function that returns names, wikipedia summaries, and wikipedia links in documents
from wikigrabber import gatherer as gr

from dbfunc import dbinsert, dbquery

#define constants
UPLOAD_FOLDER = 'test_files'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'docx', 'doc'])

#create a flask instance 
app = Flask(__name__)

#configure constant upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#check for correct file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#render homepage
@app.route('/')
def index():
	return render_template('index.html')

#render second page
@app.route('/secondpage')
def secondpage():

	#adapted from http://stackoverflow.com/questions/185936/delete-folder-contents-in-python
	#delete all old files when renderding second page to ensure new upload screen for user
	for the_file in os.listdir(UPLOAD_FOLDER):
	    file_path = os.path.join(UPLOAD_FOLDER, the_file)
	    try:
	        if os.path.isfile(file_path):
	            os.unlink(file_path)
	    except Exception, e:
	        print e
	return render_template('secondpage.html')

#upload files, adapted from http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
@app.route('/uploader', methods=['GET', 'POST'])
def uploader():

	#ensure POST request
	if request.method == 'POST':
		files = request.files.getlist('file')
		filenames = []
		
		#take user files and save in upload folder
		for f in files:
			if f and allowed_file(f.filename):
				filename = secure_filename(f.filename)
				f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				filenames.append(filename)
		return 'OKAY'

	#prevent GET requests for second page
	if request.method == 'GET':
	  	return redirect(url_for('index'))

#render third page
@app.route('/thirdpage', methods=['GET', 'POST'])
def thirdpage():
	
	#render error screen if user does not upload files
	if request.method == 'POST':
		if not os.listdir(UPLOAD_FOLDER):
			return render_template('error.html')
		
		#create dictionary of named entities	
		else:
			namedidentities = gr()
			print "namedidentities:"
			print namedidentities
			for i in namedidentities.values():
				print i[0][0]
			dbinsert(namedidentities)

			# pass named entities to template
			return render_template('thirdpage.html', wiki=namedidentities)
	
	#prevent GET requests for third page
	if request.method == 'GET':
		# if theres a qeury, return results
		searchword = request.args.get('q', '')
		if searchword:
			namedidentities = dbquery(searchword)
			if namedidentities:
				return render_template('thirdpage.html', wiki=namedidentities)
			else:
				return render_template('emptysearch.html')
	  	return redirect(url_for('index'))

#run app and use debugger to check Flask errors  
if __name__ == '__main__':
	app.run(debug = True)
