#!/usr/bin/python

import sys
import os
import json
import csv
from optparse import OptionParser

def load_json_template(input):
	f = open(input) 
	data = json.load(f)
	return data

def load_query_srrs(input):
	samples = []
	with open(input) as f:
		for line in f:
			line = line.rstrip("\n")
			samples.append(line)
	return samples

def match_lib_to_run(input):
	return_me = {}
	with open(input) as tsv_file:
		tsv_reader = csv.reader(tsv_file, delimiter = "\t")
		counter = 0
		header = []
		for row in tsv_reader:
			counter += 1
			if (counter == 1):
				header = row
				continue
			stuff = dict(zip(header, row))
			return_me[stuff['LibraryName']] = stuff['Run']
			#print("%s,%s"%(stuff['Run'], stuff['LibraryName']))
	return return_me

def extract_info_fig_s1(query_srr, library_to_run, fig_s1):
	return_me = {}
	with open(fig_s1) as tsv_file:
		tsv_reader = csv.reader(tsv_file, delimiter = "\t")
		counter = 0
		header = []
		for row in tsv_reader:
			counter += 1
			if (counter == 1):
				header = row
				continue
			stuff = dict(zip(header, row))
			id = stuff['id'].replace('-', '_')
			srr_id = library_to_run[id]
			return_me[srr_id] = stuff
			#print("%s,%s"%(id, srr_id))
	return return_me

def main():
	parser = OptionParser()
	parser.add_option("-o", "--out_dir", help="Output directory where JSON are written to")
	(args, options) = parser.parse_args()

	dirname = os.path.dirname(__file__)
	srr_30 = os.path.join(dirname, '../input/srr.input') #SRRs to use
	srr_entrez_csv_384 = os.path.join(dirname, '../input/384-SRR-cannabis.tsv') #CSV with all 384 SRRs from study
	fig_s1 = os.path.join(dirname, '../input/File_S1.tsv') #supplemental fig s1 from paper
	template_json = os.path.join(dirname, '../input/template.json')

	cannabinoid_term_map = {
		'CBC (%)' : "cbc_percent",
		'THCA (%)' : "thc_percent",
		'CBDA (%)' : "cbd_percent",
		'CBGA (%)' : "cbg_percent"}

	#divide each of these by 10000 to get %:
	#we seem to be missing 3 of these (commented out below)
	terpene_term_map = {
		'3.carene (ppm)' : "carene",
		'A.pinene (ppm)' : "alpha_pinene",
		'A.terpinene (ppm)' : "alpha_terpinene",
		'B.caryophyllene (ppm)' : "beta_carophyllene",
		'Camphene (ppm)' : "camphene",
		'Caryophyllene.Oxide (ppm)' : "carophyllene_oxide",
	#	'Citronellol (ppm)':,
	#	'Eucalyptol (ppm)':,
		'Geraniol (ppm)' : "geraniol",
		'G.terpinene (ppm)' : "gamma_terpinene",
		'Linalool (ppm)' : "linalool",
	#	'Linalyl.Acetate (ppm)':,
		'Ocimene.1 (ppm)' : "ocimene"}

	#step1: load query SRRs
	query_srr = load_query_srrs(srr_30)
	#step2: match LibraryName to Run
	library_to_run = match_lib_to_run(srr_entrez_csv_384)
	#step3: extract information from Figure S1
	fig_s1_data = extract_info_fig_s1(query_srr, library_to_run, fig_s1)
	template_json = load_json_template(template_json)
	#step4: print out all the JSON files
	os.makedirs(args.out_dir, exist_ok=True)
	for srr in query_srr:
		j = template_json
		if srr in fig_s1_data:
			for c,v in cannabinoid_term_map.items():
				if fig_s1_data[srr][c]:
					j['cannabinoids'][v] = fig_s1_data[srr][c]
			for t,v in terpene_term_map.items():
				if fig_s1_data[srr][t]:
					j['terpenes'][v] = float(fig_s1_data[srr][t])/10000
		f = open("%s/%s.json"%(args.out_dir, srr), "w")
		f.write(json.dumps(j, indent=4, sort_keys=True))
		f.close()
	#print(fig_s1_data)

if __name__ == '__main__':
	main()