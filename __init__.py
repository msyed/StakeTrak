#to delete files
import os, shutil, sqlite3

from copy import copy

#web application framework written in python
from flask import Flask, abort, session, request, url_for, make_response, redirect, render_template

#to restrict types of files
from werkzeug import secure_filename

#personal python function that returns names, wikipedia summaries, and wikipedia links in documents
from wikigrabber import gatherer as gr

from articles import getArticles

from dbfunc import dbcustomdata, dbinsert, dbquery, trymakeusertable, delete_entity_by_id, get_entity_name_by_id

from summarizer import FrequencySummarizer 

import nlp3

from extractText import extractText

from RAKE import rake


PRODUCTION = True
try:
	os.chdir('var/www/staketrak/staketrak')
except OSError:
	PRODUCTION = False

#define constants
UPLOAD_FOLDER = 'test_files'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'docx', 'doc'])

MAX_SENT_PER_ENTITY = 10
MAX_TAGS_PER_ENTITY = 20
MAX_MENTIONS_PER_ENTITY = 20

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
@app.route('/', methods=['GET'])
def home():
	return render_template('home.html', cwd=(os.getcwd()))

#render login
@app.route('/app', methods=['GET', 'POST'])
def login():

	trymakeusertable()

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
		#print "RENDER_TEMPLATE:"
		#print render_template('index.html', username=session['username'])
		#print "USERNAME:"
		#print session['username']
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
	files = os.listdir(UPLOAD_FOLDER)
	for the_file in files:
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

@app.route('/customdata', methods=['POST', 'GET'])
def customdata():
	data = request.args.get('data', '')
	## write data to db
	dbcustomdata(1, data)
	return redirect(url_for('index'))

#render third page
@app.route('/thirdpage', methods=['GET', 'POST'])
def thirdpage():
	if not ((request.args.get('apikey', '') == "rollthru") or ('username' in session)):
		print (not 'username' in session)
		return abort(404)
	#render error screen if user does not upload files
	if request.method == 'POST':
		if not os.listdir(UPLOAD_FOLDER):
			return render_template('error.html')

		#get file names from folder of files
		else:
			#print "GETTING FILENAMES"
			namedidentities = {}
			filenames = os.listdir('test_files/') 
			total_entity_list = []
			#remove hidden files
			for i in filenames:
				if i[0] == '.':
					filenames.remove(i)
			#iterate through each file and run wikigrabber function	
			for info in filenames:
				#create dictionary of named entities	
				summarizer = FrequencySummarizer()
				text = extractText("test_files/" + info)
				if info.split('.')[-1] == "pdf":
					text = text.decode('utf8')
				summary = summarizer.summarize(text, 3)
				#newsummary = ""
				#for i in summary:
				#	newsummary += i
				entities = nlp3.get_entity_names(text, "entity_stoplist.txt")
				print entities
				entitiescopy = copy(entities)
				#location = info.replace("test_files/","")
			 	keywordobj = rake.Rake("RAKE/SmartStoplist.txt")
			 	keywords = keywordobj.run(text)
			 	#print "ENTITIES:"
			 	#print entities
				for entity in entities:
					#temp = deepcopy(entity)
					#print temp
					# TODO could have more than one file with same name uploaded
				# NOTE: REIMPLEMENT WHEN API CALL LIMIT GETS FIXED instead of aove for loop
				# for entity in entities:
				# 	# find articles based on each named entity
				# 	articles = getArticles('%s' % entity)
				# 	namedidentities[count] = [entity, newsummary, keywords, info, articles[0], articles[1], articles[2], articles[3], articles[4]]
				# 	count += 1 
					#print entities
					entitysummaries = nlp3.sentextract(text, entity, MAX_SENT_PER_ENTITY)
					entitiescopy.remove(entity)
					if entity.lower() in namedidentities.keys():
						old_ent = namedidentities[entity.lower()]
						new_ent = [old_ent[0] + entitysummaries, list(set(old_ent[1] + keywords)), list(set(old_ent[2] + [info])), list(set(old_ent[3] + entitiescopy))]
						namedidentities[entity.lower()] = new_ent
					else:
						namedidentities[entity.lower()] = [entitysummaries, keywords, [info], entitiescopy]
					#print "PLease let Barack be here"
					entitiescopy.append(entity)
					#print entities

				# At this point, namedidenties is all of the named entities for a given file:
				# {'Name': [[summaries], [keywords], [filename], [relatedeEntities]]}

				# pass named entities to template
				# print namedidentities.values()
				names_ids_tags_mentions = dbinsert(namedidentities, MAX_TAGS_PER_ENTITY, MAX_MENTIONS_PER_ENTITY)

				entities_with_ids_tags_mentions = []
				assert(len(names_ids_tags_mentions) == len(namedidentities.keys()))
				for new_entity_values in names_ids_tags_mentions:
					#                                            ID                       NAME                     SUMMARY                               KEYWORDS       LOCATIONS                                  RELATED_ENTITIES
					entities_with_ids_tags_mentions.append([new_entity_values[1], new_entity_values[0], namedidentities[new_entity_values[0]][0], new_entity_values[2], namedidentities[new_entity_values[0]][2], new_entity_values[3]])
				namedidentities = {}
				total_entity_list = total_entity_list + entities_with_ids_tags_mentions

			# entities_with_id:
			# [[72, 'NAME', ['summary'], [('key', 6.9)], ['location.txt'], ['related_1', 'related_2'], ...]
			print "TOTAL_ENTITY_LIST[0]"
			print total_entity_list[0]
			return render_template('thirdpage.html', wiki=total_entity_list, filenames1=filenames)
		
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

@app.route("/clean", methods=['POST'])
def clean():
	to_clean_id = request.args.get('id', '')
	print to_clean_id
	if request.method == 'POST':
		conn = sqlite3.connect("ASG.db")
		c = conn.cursor()
		entity = get_entity_name_by_id(c, to_clean_id)
		entity = entity.encode('utf-8')
		#print entity
		with open("entity_stoplist.txt", "a") as f:
			f.write("{}\n".format(entity))
		delete_entity_by_id(c, to_clean_id)
		conn.commit()
		conn.close()
	return "200 - OK!"
		

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
