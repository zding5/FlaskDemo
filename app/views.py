from flask import render_template, redirect, url_for, jsonify, request
from app import app, db
from .models import Picture, Survey, Useroutfits
from .forms import surveyForm, outfitForm
import json
import os, operator
import pickle
import numpy as np
import pickle
import heapq as hq
from sklearn.cluster import KMeans


LOCAL_MALLET_APP = "mallet-2.0.8RC3/bin/mallet"

topics = None
items = None
phiMatrices = None
toppage1 = None
toppage3 = None
topItemsByTopic = None
top100 = None
classified_top100 = None

url2lab_file = "data/labelLookupNew.p"
url2jpg_file = "data/jpg2Url.p"

url2lab = None
url2jpg = None
jpg2lab = dict()

km = dict()
# numk = 5
numk = 10

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():

	if request.method == "POST":
		global topics
		global items
		global phiMatrices
		global topItemsByTopic
		topics, items, phiMatrices, topItemsByTopic = getTopics()
		
		url2lab = pickle.load(open(url2lab_file, "rb"))
		url2jpg = pickle.load(open(url2jpg_file, "rb"))
		# jpg2lab = dict()
		for k in url2lab.keys():
			if k in url2jpg.keys():
				jpgname = url2jpg[k]
				jpg2lab[jpgname] = url2lab[k]

		return "done"
	return render_template("index.html")

@app.route('/page1', methods=['GET','POST'])
def survey_page1():

	form = outfitForm()
	if form.validate_on_submit():
		outfits = Useroutfits(outfit_one=form.outfit_one.data, outfit_two=form.outfit_two.data, outfit_three=form.outfit_three.data)
		db.session.add(outfits)
		db.session.commit()
	
		comp_str = form.outfit_one.data+" "+form.outfit_two.data+" "+form.outfit_three.data
		file_saver_local("concrete", comp_str)
		mallet_runner_local("concrete")
		global topics
		global phiMatrices
		global toppage1
		toppage1 = getItemsByStyle(topics,phiMatrices,"concrete")
		print(toppage1)
		return redirect(url_for('survey_page2'))
	return render_template('page1.html', form=form)


@app.route('/page2', methods=['GET', 'POST'])
def survey_page2():
	return render_template('page2.html', results=toppage1)

@app.route('/page3', methods=['GET','POST'])
def survey_page3():
	print(request.form)
	form = surveyForm(request.form)
	if form.validate_on_submit():
		print(form.event.data)
		survey_result = Survey(event=form.event.data,
							location=form.location.data,
							weather=form.weather.data,
							style=form.style.data)
		db.session.add(survey_result)
		db.session.commit()

		comp_str = form.event.data+" "+form.location.data+" "+form.weather.data+" "+form.style.data
		file_saver_local("abstract", comp_str)
		mallet_runner_local("abstract")
		global topics
		global phiMatrices
		global toppage3
		toppage3 = getItemsByStyle(topics,phiMatrices,"abstract")
		print(toppage3)
		global top100
		result_words = toppage3[list(toppage3.keys())[0]]
		top100, allwords = ComputeMatch(jpg2lab, result_words)
		# print(top100)
		global classified_top100
		classified_top100 = classify_tops(top100)
		for item in classified_top100:
			print(item)
		# bin_dict = gen_binary_lists(allwords, top100)
		# global km
		# km = kmeans_clustering(allwords, bin_dict, k=numk)

		return redirect(url_for('survey_page4'))
	
	return render_template('page3.html', form=form)


@app.route('/page4', methods=['GET','POST'])
def survey_page4():
	# for label in km.keys():
		# print("cluster"+str(label))
		# for key in km[label]:
			# print(key, jpg2lab[key])
		# print("\n\n\n")

	# return	render_template('page4.html', results=km, numk=numk)
	return render_template('page4.html', top100=classified_top100)


@app.route('/thankyou', methods=['GET','POST'])
def thankyou():
	return render_template("thankpage.html")

def file_saver_local(AorC, str):
	if AorC == "concrete":
		with open("app/mallet/concrete_words.txt", "w") as f:
			f.write(str)
	else:
		with open("app/mallet/abstract_words.txt", "w") as f:
			f.write(str)


def mallet_runner_local(AorC):
	command1 = "mallet-2.0.8RC3/bin/mallet import-file --input app/mallet/concrete_words.txt --output app/mallet/concrete_out.sequences --keep-sequence --token-regex '[\p{L}\p{P}\p{N}]*\p{L}' --use-pipe-from app/mallet/concrete.sequences"
	command2 = "mallet-2.0.8RC3/bin/mallet infer-topics --input app/mallet/concrete_out.sequences --inferencer app/mallet/inferencer-1.output.0 --output-doc-topics app/mallet/c2adoctops"

	command3 = "mallet-2.0.8RC3/bin/mallet import-file --input app/mallet/abstract_words.txt --output app/mallet/abstract_output.sequences --keep-sequence --token-regex '[\p{L}\p{P}\p{N}]*\p{L}' --use-pipe-from app/mallet/abstract.sequences"
	command4 = "mallet-2.0.8RC3/bin/mallet infer-topics --input app/mallet/abstract_output.sequences --inferencer app/mallet/inferencer-1.output.1 --output-doc-topics app/mallet/a2cdoctops"

	if AorC == "concrete":
		os.system(command1)
		print("done")
		os.system(command2)
		print("done2")

	else:
		os.system(command3)
		print("done3")
		os.system(command4)
		print("done4")
	return

def dataPreprocessing(labels,keyfile,wordweightfile):
	topics = {}
	with open(keyfile) as f:
		for lines in f:
			if len(lines.split('\t')) == 2:
				data = lines.split('\t')
				topics[data[0]] = {}
				topics[data[0]]['weight'] = float(data[1].strip())
	with open(wordweightfile) as f:
		for lines in f:
			line = lines.split('\t')
			if 'data' not in topics[line[0]]:
				topics[line[0]]['data']={}
				for l in labels:
					topics[line[0]]['data'][l]={}
			for l in labels:
				if line[1] in labels[l]:
					topics[line[0]]['data'][l][line[1]] = float(line[2].strip())
	print(topics.keys())
	for t in topics:
		topics[t]['totalweight']={}
		for l in topics[t]['data']:
			topics[t]['totalweight'][l]=0
			for elt in topics[t]['data'][l]:
				topics[t]['totalweight'][l]+= topics[t]['data'][l][elt]
	items = {}
	for t in topics:
		for l in topics[t]['data']:
			if l not in items:
				items[l]=set()
			items[l] = items[l] | set(topics[t]['data'][l].keys())
	return (topics,items)

def getTopics():
	phiMatrices = {}
	# numTopics = 150
	numTopics = 50
	labels = dict()
	labels['concrete'] = pickle.load(open("app/mallet/concrete.p","rb"))
	labels['abstract'] = pickle.load(open("app/mallet/abstract.p","rb"))

	# wordweightfile = "/Users/vaccaro/mallet-2.0.8RC2/gridsearch/UIST/results/" + str(numTopics) +"/topicWordWeight.output"
	wordweightfile = "app/mallet/topicWordWeight.output"
	# keyfile = "/Users/vaccaro/mallet-2.0.8RC2/gridsearch/UIST/results/" + str(numTopics) +"/icmsdkeys.txt"
	keyfile = "app/mallet/icmsdkeys.txt"
	(topics,items)= dataPreprocessing(labels,keyfile,wordweightfile)
	for j in range(numTopics):
		jj = str(j)
		for l in topics['0']['data']:
			vals = np.array([i/float(topics[jj]['totalweight'][l]) for i in topics[jj]['data'][l].values()])
			try:
				phiMatrices[l]=np.vstack((phiMatrices[l],vals))
			except:
				phiMatrices[l]=vals
	topItemsByTopic = {}
	for t in topics:
		if t not in topItemsByTopic:
			topItemsByTopic[t]={}
		for l in topics['0']['data']:
			res = topics[t]['data'][l]
			sortres = sorted(res.items(),key=operator.itemgetter(1))
			topItemsByTopic[t][l]=[i for i in reversed(sortres[-25:])]
	return (topics, items, phiMatrices, topItemsByTopic)


def getItemsByStyle(topics,phiMatrices,AorC):
	inferredTheta = {}
	if AorC == "concrete":
		thetafile = "app/mallet/c2adoctops"
    # thetafile = AWS_MALLET_FILES+"c2adoctops"
	else:
		thetafile = "app/mallet/a2cdoctops"
    # thetafile = AWS_MALLET_FILES+"a2cdoctops"
	with open(thetafile,"r") as f:
		for lines in f:
			data = lines.split('\t')
			try:
				float(data[0])
				if data[1] not in inferredTheta:
                    # print data
					inferredTheta[data[1]] = [float(i.strip()) for i in data[2:]]
            # print inferredTheta[data[1]]
			except:
				count = 0
	topItemsByStyleWord = {}
	for sty in inferredTheta:
		# inferredTheta[sty]=[i if i > np.mean(inferredTheta[sty]) + 2*np.std(inferredTheta[sty]) else 0 for i in inferredTheta[sty]]
		inferredTheta[sty]=[i if i > np.mean(inferredTheta[sty]) + 1.5*np.std(inferredTheta[sty]) else 0 for i in inferredTheta[sty]]

		if AorC == "concrete":
			l = "abstract"
		else:
			l = "concrete"
		topItemsByStyleWord[sty]={}
		#            for lang in phiMatrices:
		rawres = np.dot(inferredTheta[sty],phiMatrices[l])
		itemnames = list(topics['0']['data'][l].keys())
		inds = sorted(range(len(rawres)), key=lambda k: rawres[k])
		tempres = [itemnames[i] for i in reversed(inds[-25:])]
		topItemsByStyleWord[sty]=tempres
		print(inferredTheta)
	return topItemsByStyleWord


def fixed_heap_insert(h, size, input):
	if len(h) < size:
		hq.heappush(h, input)
	else:
		if input > h[0]:
			hq.heappushpop(h, input)
	return h

def ComputeMatch(lookup, tags):
	tags = set(tags)
	tops = []
	allwords = set()
	for k, v in lookup.items():
		cur_score = 0
		intersection = []
		union = []
		v_set = set(v)
		intersection = tags & v_set
		union = tags | v_set
		cur_score = float(len(intersection)/len(union))
		fixed_heap_insert(tops, 100, (cur_score,(k,v)))
		allwords = allwords | v_set
	print("Done Matching")
	return sorted(tops), allwords

def to_binary_list(allwords, outfit):
	allwords = list(allwords)
	bin_list = np.zeros(len(allwords), dtype=np.int8)
	for word in outfit:
		bin_list[allwords.index(word)] = 1
	return bin_list

def gen_binary_lists(allwords, tops):
	allwords = list(allwords)
	bin_dict = dict()
	for outfit in tops:
		print(outfit[1][0])
		bin_dict[outfit[1][0]] = to_binary_list(allwords, outfit[1][1])
	return bin_dict

def kmeans_clustering(allwords, bin_dict, k=4):
	arr = np.empty((0,len(allwords)), int)
	cluster = KMeans(init='k-means++', n_clusters=k, n_init=10)
	for key in bin_dict.keys():
		arr = np.append(arr, [bin_dict[key]], axis=0)
	print(arr)
	results = cluster.fit_predict(arr)
	cluster_dict = dict()
	print(type(k))
	for i in range(k):
		cluster_dict[i] = []
	keys = list(bin_dict.keys())
	#     print(keys)
	for i in range(len(results)):
		cluster_dict[results[i]].append(keys[i])
	return cluster_dict


def classify_tops(tops):
	classified = dict()
	for item in tops:
		cate = find_most_freq(item[1][1])
		classified.setdefault(cate, []).append(item[1])
	print(classified)
	return classified


def find_most_freq(alist):
	s_alist = sorted(alist)
	most_freq = ""
	max_count = 0
	cur_word = ""
	cur_count = 0
	for word in s_alist:
		if word != cur_word:
			cur_word = word
			cur_count = 1
		else:
			cur_count += 1
		if cur_count > max_count:
			max_count = cur_count
			most_freq = cur_word
	print(most_freq)
	return most_freq



















