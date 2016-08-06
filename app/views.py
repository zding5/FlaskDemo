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
import operator
import string


LOCAL_MALLET_APP = "mallet-2.0.8RC3/bin/mallet"

topics = None
items = None
phiMatrices = None
toppage1 = None
toppage3 = None
topItemsByTopic = None
top100 = None
classified_top100 = None

jpg2lab_file = "data/needed_jpg2lab.p"

url2lab = None
url2jpg = None
jpg2lab = dict()

labels = dict()
wholeVocab = set()


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():

	if request.method == "POST":
		global topics
		global items
		global phiMatrices
		global topItemsByTopic
		global jpg2lab
		print("what3?")
		topics, items, phiMatrices, topItemsByTopic = getTopics()
		jpg2lab = pickle.load(open(jpg2lab_file, "rb"))

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

		survey_result = Survey(event = form.event.data)
		db.session.add(survey_result)
		db.session.commit()

		comp_str = form.event.data

		# finalDoc = []
		# dind = []
		# text1 = (comp_str.translate(str.maketrans({key: None for key in string.punctuation}))).split()
		# for i in range(len(text1)):
		# 	if i not in dind:
		# 		for n in list(reversed(range(1,5))):
		# 			if i not in dind:
		# 				nGrams(n, i, text1, wholeVocab, finalDoc, dind)
		# print(finalDoc)
		# final_comp_str = ""
		# for word in finalDoc:
		# 	final_comp_str = final_comp_str + word + " "

		file_saver_local("abstract", comp_str)
		# file_saver_local("abstract", final_comp_str)
		mallet_runner_local("abstract")
		global topics
		global phiMatrices
		global toppage3
		toppage3 = getItemsByStyle(topics,phiMatrices,"abstract")
		global top100
		result_words = toppage3[list(toppage3.keys())[0]]
		top100, allwords = ComputeMatch(jpg2lab, result_words)
		global classified_top100
		classified_top100 = classify_tops(top100, at_least_num_items=5)

		return redirect(url_for('survey_page4'))
	
	return render_template('page3.html', form=form)


@app.route('/page4', methods=['GET','POST'])
def survey_page4():
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
	numTopics = 50
	global labels
	global wholeVocab
	labels['concrete'] = pickle.load(open("app/mallet/concrete.p","rb"))
	labels['abstract'] = pickle.load(open("app/mallet/abstract.p","rb"))
	wholeVocab = labels['concrete'] | labels['abstract']

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


def classify_tops(tops, at_least_num_items):
	classified = dict()
	for item in tops:
		# cate is the most frequent label in the set, used as key
		cate = find_most_freq(item[1][1])
		classified.setdefault(cate, []).append(item[1])
	
	sorted_classified = sorted(classified.items(), key=operator.itemgetter(1))
	reduced_sorted_classified = [x for x in sorted_classified if len(x[1]) >= 5]

	print(reduced_sorted_classified)
	return reduced_sorted_classified


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
	return most_freq


def nGrams(n, i, text, vocab, finalDoc, dind):
	sub = text[i:i+n]
	ngram = "-".join(sub)
	if ngram in vocab:
		print(ngram)
		finalDoc += [ngram]
		dind.append(list(range(i, i+n)))
















