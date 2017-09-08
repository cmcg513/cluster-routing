from difflib import SequenceMatcher
import csv
import string

def sim(a,b):
	ratio = SequenceMatcher(None,a,b).ratio()
	return ratio > 0.5

def read_file(filename):
	data = []
	with open(filename,'r') as data_file:
		i = 0
		reader = csv.reader(data_file,delimiter=",",quotechar="\"")
		for row in reader:
			if i == 0:
				i += 1
				continue
			i += 1
			name = row[5]
			address = row[9]
			# zip_code = row[8]
			# town = row[7]
			# apt = row[10]
			data.append([i,name,address])#,town,zip_code,apt])
	return data

def replace_all(s,strip_words):
	for w in strip_words:
		s = s.replace(w,"")
	return s

def process(data):
	strip_words = ['avenue','ave','street','boulevard','blvd','st','road','rd','court','ct','guest','guests','family','spouse','spouses']
	translator = str.maketrans({key: None for key in string.punctuation})
	for i in range(len(data)):
		indx,name,addr = data[i] #,zipc,twn,apt
		name = name.translate(translator)
		addr = addr.translate(translator)
		name = name.lower()
		addr = addr.lower()
		name = replace_all(name,strip_words)
		addr = replace_all(addr,strip_words)
		matches = []
		for j in range(i + 1,len(data)):
			n_indx,n_name,n_addr = data[j] #,n_zipc,n_twn,n_apt
			n_name = n_name.translate(translator)
			n_addr = n_addr.translate(translator)
			n_name = n_name.lower()
			n_addr = n_addr.lower()
			n_name = replace_all(n_name,strip_words)
			n_addr = replace_all(n_addr,strip_words)
			print(addr,n_addr)
			if sim(name,n_name) and sim(addr,n_addr):
				matches.append(data[j])
		if len(matches) > 0:
			tmp = "%d: %s, %s"
			s1 = tmp % tuple(data[i])
			s2 = "*"*15
			print(s1)
			print(s2)
			for m in matches:
				print(tmp % tuple(m))
			print("\n")

def main():
	data = read_file("raw_data.csv")
	process(data)

main()