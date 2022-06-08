from html.parser import HTMLParser
import requests, sys

LorE = False
debug = False
simpler = False
key = ""
dictionary = {}
class MyHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		global key
		global LorE
		if tag=="th":
			LorE = False

		elif tag=="td":
			LorE = True
	def handle_endtag(self, tag):
		pass

	def handle_data(self, data):
		global LorE
		global key
		global dictionary
		if(LorE):
			dictionary[key] = data
		else:
			key = data

def update():
	URL = "https://ampersandia.net/roxy/laiqbun/laiqbun-dictionary.html"
	print( "Downloading from", URL+"...")
	try:
		response = requests.get(URL)
		open("laiqbun-dictionary.html", "wb").write(response.content)
		return False
	except requests.exceptions.ConnectionError:
		print("Error, unable to connect!")
		return True
def load():
	global dictionary
	print("Loading...")
	f = open("laiqbun-dictionary.html")
	for line in f:
		parser.feed(line)

digitTranslation = {
	"ku":"0",
	"kku": "1",
	"gu": "2",
	"tu": "3",
	"ttu": "4",
	"du": "5",
	"lu": "6",
	"ru": "7",
	"mu": "8",
	"nu": "9",
	"pu": "X",
	"ppu": "Y"
}
particleTranslation = {
	"gyn": " and ",
	"kyo":" but ",
	"kyn": "«",
	"lyq": "»",
	"kye": "(",
	"nye":")",
	"ppykun":"[",
	"ppylun":"]",
	"zyem":"+",
	"ryeq":"-",
	"vyuq": "*",
	"lyau": "/",
	"ppyua": "^",
	"cya": "root of "
}


def partOfSpeech(word):
	if(len(word)>1 and word[1]in "aeiouy"):
		return word[1]
	elif (len(word)>2 and word[2] in "aeiouy"):
		return word[2]
	else:
		return "n"

def handleParticle(word):
	try:
		return particleTranslation[word]
	except KeyError:
		return "{"+dictionary[word].strip(" ")+"}"

def parseNumber(x):
	x = x.replace("kuyq", ";").replace("puyq", ";").replace("vuyn", ";").replace("tuyq", ";")
	digits = x.split(";")
	out = ""
	for digit in digits:
		try:
			out = digitTranslation[digit]+out
		except KeyError:
			out = "?"+out
	return out

def handleNoun(word):
	if(word[0:4]=="haiq"):
		return parseNumber(word[4:])
	temp = word.replace("a","e",1)
	out = ""

	if temp in dictionary:
		temp = dictionary[temp]
		if temp[:5]=="x1 is":
			out = temp.replace("x1 is", "")
		else:
			out = temp.replace("x1", "that which")
		return out.strip(" ")
	else:
		return "["+word+"]"

def substituteNouns(statement, nouns):
	if(debug):
		print("Statement",statement)
	for i in range(len(nouns)):
		if(debug):
			print("> substitute:\"", nouns[i], "\" for:",  "x"+str(i+1))
		if(not simpler):
			statement= statement.replace("x"+str(i+1), "("+nouns[i]+")")
		else:
			statement= statement.replace("x"+str(i+1), nouns[i])

	return statement

def parseQuery(query):
	out = ""
	statement = "x1"
	construction = []
	nouns = []
	statementIndex = -1
	sentences = query.split(".")
	for sentence in sentences:
		sentence = sentence.strip(" ")
		words = sentence.lower().split(" ")
		i = 0;
		while(i<len(words)):
			pos = partOfSpeech(words[i])
			if pos=="y" and words[i] in dictionary:
				#if(words[i] in ["zy", "gyn", "kyo"]):
				if (not words[i] in ["ly", "my", "py", "ty", "hy"]):
					statement = substituteNouns(statement, nouns)
					if(not statement=="x1"):
						construction.append(statement)
					statement = "x1"
					nouns = []

					construction.append(handleParticle(words[i]))
			elif pos =="e" and words[i] in dictionary:
				predicate = dictionary[words[i]]
				if( not simpler):
					predicate = "("+predicate+")"
				try:
					if(words[i-1]=="ly"):
						for k in range(3):
							predicate = predicate.replace("x"+str(3-k), "x"+str(4-k))
					elif(words[i-1]=="my"):
						predicate = predicate.replace("x1 is", "x1").replace("s ", "ed ", 1).replace("x1", "x1 was").replace("x2", "by x2")
					elif(words[i-1]=="ty"):
						predicate = predicate.replace("x2", "itself")
					if(words[i-1]=="hy"):
						predicate = predicate.replace("x1 is", handleNoun(words[i-2]))
					elif(words[i-1]=="py"):
						for k in range(3):
							predicate = predicate.replace("x"+str(3-k), "x"+str(4-k))
						predicate = predicate.replace("x2", "x1 in degree of x2" )
				except IndexError:
					pass

				if("x2" in statement):
					statement = statement.replace("x2", predicate )
				else:
					statement = statement.replace("x1", predicate)
			elif pos == "a":
				noun = handleNoun(words[i])
				try:
					if(partOfSpeech(words[i+1])=="e" and words[i+1] in dictionary):
						noun += " "+dictionary[words[i+1]].replace("x1", "which")
						i+=1
				except IndexError:
					pass
				nouns.append(noun)
			elif pos=="i":
				clause = "that "+dictionary[words[i].replace("i", "e", 1)]
				clauseArguments = []
				while(words[i]!="gy"):
					i += 1
					if(partOfSpeech(words[i])=="a"):
						noun = handleNoun(words[i])
						try:
							if(partOfSpeech(words[i+1])=="e" and words[i+1] in dictionary):
								noun += " "+dictionary[words[i+1]].replace("x1", "which")
								i+=1
						except IndexError:
							pass
						clauseArguments.append(noun)
					elif(partOfSpeech(words[i])=="e"):
						if("x2" in clause):
							clause = clause.replace("x2", dictionary[words[i]] )
						else:
							clause = clause.replace("x1", dictionary[words[i]])

				clause = substituteNouns(clause, clauseArguments)
				nouns.append(clause)
			elif pos=="o":
				clause = dictionary[words[i].replace("o", "e", 1)]
				clauseArguments = []
				try:
					described = handleNoun(words[i-1])+" that"
					nouns.pop()
				except IndexError:
					described = "x1"


				while(words[i]!="gy"):
					i += 1
					if(words[i]=="kka"):
						clauseArguments.append(described)
					elif(partOfSpeech(words[i])=="a"):
						clauseArguments.append(handleNoun(words[i]))
				clause = substituteNouns(clause, clauseArguments)
				nouns.append(clause)
			else:
				nouns.append("{"+words[i]+"}")
			i +=1
		statement = substituteNouns(statement, nouns)

		if(not statement=="x1"):

			construction.append(statement)
		for w in construction:
			out += w + " "
		out =out.strip(" ")+". "

	return out.replace("x1", "<x1>").replace("x2", "<x2>").replace("x3", "<x3>").replace("x4", "<x4>").replace("x5", "<x5>")

if (__name__ == "__main__"):
	parser = MyHTMLParser()

	for arg in sys.argv	:
		if(arg=="-u"):#force update
			if(update()):
				quit()
			print("Update successful!")
			quit()
		elif(arg=="-d"): #simpler translations
			debug = True
		elif(arg=="-s"): #simpler translations
			simpler = True
	try:
		load()
	except FileNotFoundError:
		print("Dictionary missing!")
		if(update()):
			quit()
		load()
	print("Ready.")
	while(True):
		print(parseQuery(input("Laiqbun: ")))
