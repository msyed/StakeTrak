#to delete files
import os, shutil

#web application framework written in python
from flask import Flask, abort, session, request, url_for, make_response, redirect, render_template

#to restrict types of files
from werkzeug import secure_filename

#personal python function that returns names, wikipedia summaries, and wikipedia links in documents
from wikigrabber import gatherer as gr

from dbfunc import dbinsert, dbquery

from summarizer import FrequencySummarizer

import nlp

from extractText import extractText

from RAKE import rake

#define constants
UPLOAD_FOLDER = 'test_files'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'docx', 'doc'])

#create a flask instance 
app = Flask(__name__)

# secret keyq
app.secret_key = '\xd3\xbdMBJ\xbb\xfe\x8d\xe4\xe9\xb8\x15\xde]\xd9ei\xfb\x8f1\xb2=O\x16'

#configure constant upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#check for correct file extensions
def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#render login
@app.route('/', methods=['GET', 'POST'])
def login():

	if 'username' in session:
		return redirect(url_for('index'))

	if request.method == 'GET':
		return render_template('login.html', error=0)
		
	if request.method == 'POST':
		if (not 'username' in request.form) or (not 'password' in request.form):
			# login failed - incomplete form
			return render_template('login.html', error=1)
		
		if request.form['username'] == 'admin' and request.form['password'] == 'admin':
				session['username'] = request.form['username']
				return redirect(url_for('index'))
		else:
			# login failed - bad credentials
			return render_template('login.html', error=2)
	else:
		abort(405)

	return redirect(url_for('index'))

#render homepage
@app.route('/index', methods=['GET', 'POST'])
def index():
	if 'username' in session:
		# logged in!
		return render_template('index.html', username=session['username'])
	else:
		return abort(404)

#render second page
@app.route('/secondpage', methods=['GET', 'POST'])
def secondpage():
	if not 'username' in session:
		return abort(404)
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

@app.route('/dbsecondpage')

def dbsecondpage():
	if not 'username' in session:
		return abort(404)
	return render_template('dbsecondpage.html')

#upload files, adapted from http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
@app.route('/uploader', methods=['POST'])
def uploader():
	if not 'username' in session:
		return abort(404)
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
	return abort(404)
	#prevent GET requests for second page
	# if request.method == 'GET':
	#   	return redirect(url_for('index'))

#render third page
@app.route('/thirdpage', methods=['GET', 'POST'])
def thirdpage():
	if not 'username' in session:
		return abort(404)
	#render error screen if user does not upload files
	if request.method == 'POST':
		if not os.listdir(UPLOAD_FOLDER):
			return render_template('error.html')

	#get file names from folder of files
		else:

			count = 0
			namedidentities = {}
			filenames = os.listdir('test_files/') 
			
			#remove hidden files
			for i in filenames:
				if i[0] == '.':
					filenames.remove(i)

			#iterate through each file and run wikigrabber function	
			for info in filenames:
				#create dictionary of named entities	
				summarizer = FrequencySummarizer()
				text = extractText(info)
				summary = summarizer.summarize(text, 3)
				newsummary = ""
				for i in summary:
					newsummary += i
				entities = nlp.extract_entities2(text)
				location = info.replace("test_files/","")
			 	keywordobj = rake.Rake("RAKE/SmartStoplist.txt")
			 	keywords = keywordobj.run(text)
			 	articles = "" #insert Austin's stuff the 
				for entity in entities:
					namedidentities[count] = [entity, newsummary, keywords, location]
					count += 1 
				# pass named entities to template
				#print namedidentities.values()
			dbinsert(namedidentities)
			return render_template('thirdpage.html', wiki=namedidentities)
		
	#prevent GET requests for third page
	if request.method == 'GET':
		# if theres a query, return results
		searchword = request.args.get('q', '')
		if searchword:
			namedidentities = dbquery(searchword)
			if namedidentities:
				return render_template('thirdpage.html', wiki=namedidentities)
			else:
				return render_template('emptysearch.html')
	  	return redirect(url_for('index'))


@app.route("/logout", methods=['POST'])
def logout():
	if not 'username' in session:
		return abort(404)
	if request.method == 'POST':
		if 'username' in session:
			session.pop('username', None)
	return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#run app and use debugger to check Flask errors  
if __name__ == '__main__':
	app.run(debug = True)
