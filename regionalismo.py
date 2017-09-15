import sys
import re
import csv
import time
import pickle
import math
import gensim

import asi_hablamos

from collections import deque
from os import listdir


def get_palabras(tweet, removeupper = False):

	pos = tweet.find('@ ')
	if pos >= 0:
		tweet = tweet[:pos]

	palabras=[]
	if removeupper:
		for i in tweet.split():
			if not i.istitle():
				palabras.append(i.lower())	
	else:
		palabras = tweet.lower().split()
	for idx, p in enumerate(palabras):

		if p[0] == '#' or p[0] == '@' or p.find('http') == 0:
			#print('----' + p)
			#palabras.remove(p)
			palabras[idx] = '_NOPE_'
		else:
			palabra = p
			url_pos = palabra.find("pic.twitter")
			if url_pos >= 0:
				#print('asdasdasda:    ' + palabra)
				palabra = palabra[:url_pos] 
			url_pos = palabra.find(r"http")
			if url_pos >= 0:
				#print('http:   ' + palabra)
				palabra = palabra[:url_pos]

			reg = re.compile('[^a-zA-ZáéíóúàèìòùÀÈÌÒÙÁÉÍÓÚñÑÜü]', re.UNICODE)
			palabra = reg.sub('', palabra)
			if (len(palabra) == 0):
				#print('ceero')
				palabras[idx] = '_NOPE_'
			else:
				#print('++++: ' + ''.join(str(ord(c)) + "_" for c in p) + ' len: ' + str(len(p)))
				#print('++++: ' + p + ' len: ' + str(len(p)))
				#print('++++: ' + palabra + ' len: ' + str(len(palabra)))
				palabras[idx] = palabra 
	palabras = list(filter(lambda a: a != '_NOPE_', palabras))
	return palabras

if len(sys.argv) > 2:
	if sys.argv[1] == '-f':
		paises		= {}
		ciudades	= {}
		dicc_pal	= {}
		dicc_cont	= {}
		pais_ciudad 	= {}
		indice_actual	= 0
		directorio = sys.argv[2]
		filenames = [directorio + "/" + x for x in listdir(directorio) if ".tsv" in x and "Twitter_" in x]
		timestamp = time.time()
		start_time = time.time()
		for filename in filenames:
			print(filename)
			filename_pattern=re.compile("^.+_(.+)_(.+).tsv$")
			filename_match=filename_pattern.search(filename)
			pais	= ""
			ciudad	= ""
			
			if filename_match != None:
				pais	= filename_match.group(1)
				ciudad 	= filename_match.group(2)
				if not pais in paises:
					paises[pais] = 0
				if not ciudad in ciudades:
					ciudades[ciudad] = 0
				pais_ciudad[indice_actual] = (pais, ciudad)
			else:
				print('error')
				sys.exit()

			linea = 0
			with open(filename, newline = '', encoding = 'utf-8') as archivo:
				csv_reader = csv.reader(archivo, delimiter = '\t', quotechar = None)
				primera = True
				for row in csv_reader:
					linea += 1
					if linea > 50:
						#break
						pass
					tweet = row[2]
					if primera:
						primera = False
					else:
						words			 = get_palabras(tweet, True)
						paises[pais]		+= len(words)
						ciudades[ciudad] 	+= len(words)
						for pal in words:
							if not pal in dicc_pal:
								dicc_pal[pal] = [0] * len(filenames)
							dicc_pal[pal][indice_actual] += 1
			indice_actual += 1 
		#print(dicc_pal)
			print("\t","({1}m, {0}s)".format(round(time.time()-timestamp,2),round((time.time()-start_time)/60,2)))
		for pal in dicc_pal:
			dicc_cont[pal] = sum(i>0 for i in dicc_pal[pal])
		nombre_salida = 'twitter_frecuencias'
		if len(sys.argv) > 3:
			nombre_salida = sys.argv[3]
		with open(nombre_salida + '.csv', 'w', newline = '', encoding = 'utf-8') as archivo_salida:
			csv_writer = csv.writer(archivo_salida, delimiter = '\t')
			for i in dicc_pal:
				salida = [i]
				salida.extend(dicc_pal[i])
				#print(salida)
				#print(str(dicc_pal[i]))
				#print(salida)
				csv_writer.writerow(salida)
				line=str(dicc_pal[i]).strip()
				line='"'+i+'",'+line[1:-1]+"\n"
				line='"'+i+'",'+line[1:-1]+"\n"
				#print(line)
		#print(dicc_pal.keys())
		print(len(dicc_pal.keys()))
		pick = open(nombre_salida + ".pkl","wb")
		pickle.dump([paises, ciudades, pais_ciudad,dicc_cont], pick)
		pick.close()

	if sys.argv[1] == '-r':
		pick	= open("twitter_frequencies_test.pkl", "rb")
		paises, ciudades, pais_ciudad = pickle.load(pick)
		pick.close()
		ar_csv	= open("twitter_frec_test.csv", "r")
		for linea in ar_csv:
			linea = '"' + linea
			linea = linea.replace('\t', '",', 1).replace('\t', ',')
			try:
				linea = eval("[u" + linea.strip() + "]")
				print(linea)
			except:
				continue
			palabra = linea[0]
			print(palabra)
			if palabra.istitle():
				continue
			if not palabra.isalpha():
				continue
			if palabra.isupper():
				continue
			vector_palabra = linea[1:]
			freq_relativa_vector = [word_vector[i] / city_freq_vector for i in range(len(word_vector))]

		#print(paises)
		#print(ciudades)
		#print(pais_ciudad)
	if sys.argv[1] == '-t':
		archivo = "twitter_frecuencias"
		if len(sys.argv) > 3:
			archivo = sys.argv[3] 
		timestamp = time.time()
		start_time = time.time()
		directorio = sys.argv[2]
		if directorio[-1:] != '/':
			directorio += '/'
		if len(directorio) == 1:
			directorio = ""
		pick	= open(directorio + archivo + ".pkl", "rb")
		paises, ciudades, pais_ciudad, idf = pickle.load(pick)
		pick.close()
		print(pais_ciudad)
		l_d = []
		for i in (pais_ciudad):
			l_d.append(ciudades[pais_ciudad[i][1]])

		ar_csv	= open(directorio + archivo + ".csv", "r")
		palabras = []
		frecuencia = []
		for linea in ar_csv:
			r = linea[:-1].split('\t')
			p = r[0]
			vector = r[1:]
			palabras.append(p)
			frecuencia.append(vector)
		ar_csv.close()
		print("Abrir csv " + str(time.time()-timestamp))
		timestamp =	time.time()

		#Calcular IDF
		N = len(frecuencia[0])
		for p in idf:
			idf[p] = math.log(N / idf[p])
		print("calcular idf")
		print(time.time()-timestamp)
		timestamp =	time.time()

		#Encontrar frecuencia máxima
		max_ftd = [0] * N
		for i in range(0, len(frecuencia)):
			for j in range(0,N):
				if max_ftd[j] < float(frecuencia[i][j]):
					max_ftd[j] = float(frecuencia[i][j])

		print("encontrar máxima frecuencia")
		print(time.time()-timestamp)
		timestamp =	time.time()

		m_tfidf = []
		m_tflogidf = []
		m_tfdoubleidf = []
		m_hiram = []
		m_hiramlog = []
		m_hiramd = []
		top = 200
		for i in range(0, N):
			de = deque(maxlen = top)
			de.appendleft((-1,None))
			m_tfidf.append(de)
			de = deque(maxlen = top)
			de.appendleft((-1,None))
			m_tflogidf.append(de)
			de = deque(maxlen = top)
			de.appendleft((-1,None))
			m_tfdoubleidf.append(de)

			de = deque(maxlen = top)
			de.appendleft((-1,None))
			m_hiram.append(de)
			de = deque(maxlen = top)
			de.appendleft((-1,None))
			m_hiramlog.append(de)
			de = deque(maxlen = top)
			de.appendleft((-1,None))
			m_hiramd.append(de)

		for i in range(0, len(frecuencia)):
			if i % 10000 == 0:
				print(str(i*100/len(frecuencia)) + "% " + str(int((time.time() - timestamp)/60)) + ":" + str(int(time.time() - timestamp)%60))
			for j in range(0, N):
				ftd = float(frecuencia[i][j])

				#tf 
				tf = ftd / l_d[j]
				idf_c = idf[palabras[i]]

				#tf log normalization
				if ftd != 0:
					tflog = math.log(ftd)
				else:
					tflog = 0

				#tf double normalization 0.5
				#max_ftd = ?
				tfdouble = 0.5 + 0.5 * (ftd/max_ftd[j])

				#tf-idf Tradicional
				tfidf = tf * idf_c
				#tf-idf log normalization
				tflogidf = tflog * idf_c
				#tf-idf double normalization
				tfdoubleidf = tfdouble * idf_c
				#hiram tradicional
				if tf >= 1 and idf_c >= 1:
					print(tf,idf_c)
					hiram = (1/(tf**5)) * math.log(idf_c**2 * tf**3 * (idf_c * tf**2 + 5*tf + 2 * math.log(idf_c) + math.log(tf)))
				else:
					hiram = 0
				#hiram log norm
				if tflog >= 1 and idf_c >= 1:
					hiramlog = (1/(tflog**5)) * math.log(idf_c**2 * tflog**3 * (idf_c * tflog**2 + 5*tflog + 2 * math.log(idf_c) + math.log(tflog)))
				else:
					hiramlog = 0
				#hiram double
				if tfdouble >= 1 and idf_c >= 1:
					hiramd = (1/(tfdouble**5)) * math.log(idf_c**2 * tfdouble**3 * (idf_c * tfdouble**2 + 5*tfdouble + 2 * math.log(idf_c) + math.log(tfdouble)))
				else:
					hiramd = 0

				for m in range(0, top):
					maximo = m_tfidf
					if maximo[j][m][0] < tfidf:
						if len(maximo[j]) >= top:
							maximo[j].pop()
						maximo[j].insert(m,(tfidf, palabras[i]))
						break
					maximo = m_tflogidf

					if maximo[j][m][0] < tflogidf:
						if len(maximo[j]) >= top:
							maximo[j].pop()
						maximo[j].insert(m,(tflogidf, palabras[i]))
						break
					maximo = m_tfdoubleidf
					if maximo[j][m][0] < tfdoubleidf:
						if len(maximo[j]) >= top:
							maximo[j].pop()
						maximo[j].insert(m,(tfdoubleidf, palabras[i]))
						break
					maximo = m_hiram
					if maximo[j][m][0] < hiram:
						if len(maximo[j]) >= top:
							maximo[j].pop()
						maximo[j].insert(m,(hiram, palabras[i]))
						break
					maximo = m_hiramlog
					if maximo[j][m][0] < hiramlog:
						if len(maximo[j]) >= top:
							maximo[j].pop()
						maximo[j].insert(m,(hiramlog, palabras[i]))
						break
					maximo = m_hiramd
					if maximo[j][m][0] < hiramd:
						if len(maximo[j]) >= top:
							maximo[j].pop()
						maximo[j].insert(m,(hiramd, palabras[i]))
						break
		print("calcular tfidf")
		print(time.time()-timestamp)
		timestamp =	time.time()

		f = open('tfidf.txt', 'w')
		maximo = m_tfidf
		for m in range(0,N):
			print(pais_ciudad[m][0], pais_ciudad[m][1], file=f)
			print(len(maximo[m]))
			for i in range(0,top):
				print(str(maximo[m][i][0]) + ' ' + str(maximo[m][i][1]), file=f)

		f = open('tflogidf.txt', 'w')
		maximo = m_tflogidf
		for m in range(0,N):
			print(pais_ciudad[m][0], pais_ciudad[m][1], file=f)
			for i in range(0,top):
				print(str(maximo[m][i][0]) + ' ' + str(maximo[m][i][1]), file=f)

		f = open('tfdoubleidf.txt', 'w')
		maximo = m_tfdoubleidf
		for m in range(0,N):
			print(pais_ciudad[m][0], pais_ciudad[m][1], file=f)
			for i in range(0,top):
				print(str(maximo[m][i][0]) + ' ' + str(maximo[m][i][1]), file=f)

		f = open('hiram.txt', 'w')
		maximo = m_hiram
		for m in range(0,N):
			print(pais_ciudad[m][0], pais_ciudad[m][1], file=f)
			for i in range(0,top):
				print(str(maximo[m][i][0]) + ' ' + str(maximo[m][i][1]), file=f)

		f = open('hiramlog.txt', 'w')
		maximo = m_hiramlog
		for m in range(0,N):
			print(pais_ciudad[m][0], pais_ciudad[m][1], file=f)
			for i in range(0,top):
				print(str(maximo[m][i][0]) + ' ' + str(maximo[m][i][1]), file=f)

		f = open('hiramd.txt', 'w')
		maximo = m_hiramd
		for m in range(0,N):
			print(pais_ciudad[m][0], pais_ciudad[m][1], file=f)
			for i in range(0,top):
				print(str(maximo[m][i][0]) + ' ' + str(maximo[m][i][1]), file=f)

	if sys.argv[1] == '-s':
		archivo = "twitter_frecuencias"
		if len(sys.argv) > 3:
			archivo = sys.argv[3] 
		timestamp = time.time()
		start_time = time.time()
		directorio = sys.argv[2]
		if directorio[-1:] != '/':
			directorio += '/'
		if len(directorio) == 1:
			directorio = ""

		ar_csv	= open(directorio + archivo + ".csv", "r")
		palabras	= []
		frecuencia	= []
		ciudades	= []
		paises		= []
		idf			= {}
		N			= 0
		t_d			= []

		i = 0
		for linea in ar_csv:
			i += 1
			r = linea[:-1].split(',')
			if i == 1:
				ciudades = r[6:]
				N = len(ciudades)
				t_d = [0] * N
			elif i == 2:
				paises = r[6:]
			elif i > 6:

				count_total	= int(r[1])
				count_lower = int(r[2])
				count_titled= int(r[3])
				count_upper = int(r[4])
				count_other = int(r[5])

				if count_titled > count_lower: #no proper names
					#print("a: " + str(r[0:6]))
					continue
				if count_upper > count_lower: #no acronyms
					#print("b: " + str(r[0:6]))
					continue
				if count_other > count_lower: #no other weird things
					#print("c: " + str(r[0:6]))
					continue
				p = r[0][1:-1]
				vector = [int(i) for i in r[6:]]
				palabras.append(p)
				frecuencia.append(vector)
				#calcular idf
				nt = sum(idf>0 for idf in vector)
				idf[p] = math.log(N / nt)
				#conteo total
				for c in range(0, N):
					t_d[c] += vector[c]
			if i > 5000:
				pass
				#break
		ar_csv.close()
		print("Abrir csv " + str(time.time()-timestamp))
		timestamp =	time.time()

		#Encontrar frecuencia máxima
		max_ftd = [0] * N
		for i in range(0, len(frecuencia)):
			for j in range(0,N):
				if max_ftd[j] < float(frecuencia[i][j]):
					max_ftd[j] = float(frecuencia[i][j])

		print("encontrar máxima frecuencia")
		print(time.time()-timestamp)
		timestamp =	time.time()

		m_tfidf = []
		m_tflogidf = []
		m_tfdoubleidf = []
		top = 1000
		for i in range(0, N):
			de = deque(maxlen = top)
			de.appendleft((-1,None))
			m_tfidf.append(de)
			de = deque(maxlen = top)
			de.appendleft((-1,None))
			m_tflogidf.append(de)
			de = deque(maxlen = top)
			de.appendleft((-1,None))
			m_tfdoubleidf.append(de)

		for i in range(0, len(frecuencia)):
			if i % 10000 == 0:
				print(str(i*100/len(frecuencia)) + "% " + str(int((time.time() - timestamp)/60)) + ":" + str(int(time.time() - timestamp)%60))
			for j in range(0, N):
				ftd = float(frecuencia[i][j])

				#tf 
				tf = ftd / t_d[j]
				idf_c = idf[palabras[i]]

				#tf log normalization
				if ftd != 0:
					tflog = math.log(ftd)
				else:
					tflog = 0

				#tf double normalization 0.5
				#max_ftd = ?
				tfdouble = 0.5 + 0.5 * (ftd/max_ftd[j])

				#tf-idf Tradicional
				tfidf = tf * idf_c
				#tf-idf log normalization
				tflogidf = tflog * idf_c
				#tf-idf double normalization
				tfdoubleidf = tfdouble * idf_c


				for m in range(0, top):
					maximo = m_tfidf
					if maximo[j][m][0] < tfidf:
						if len(maximo[j]) >= top:
							maximo[j].pop()
						maximo[j].insert(m,(tfidf, palabras[i]))
						break
					maximo = m_tflogidf

					if maximo[j][m][0] < tflogidf:
						if len(maximo[j]) >= top:
							maximo[j].pop()
						maximo[j].insert(m,(tflogidf, palabras[i]))
						break
					maximo = m_tfdoubleidf
					if maximo[j][m][0] < tfdoubleidf:
						if len(maximo[j]) >= top:
							maximo[j].pop()
						maximo[j].insert(m,(tfdoubleidf, palabras[i]))
						break
		print("calcular tfidf")
		print(time.time()-timestamp)
		timestamp =	time.time()

		f = open('tfidf.txt', 'w')
		maximo = m_tfidf
		for m in range(0,N):
			print(ciudades[m], paises[m], file=f)
			print(len(maximo[m]))
			for i in range(0,top):
				print(str(maximo[m][i][0]) + ' ' + str(maximo[m][i][1]), file=f)

		f = open('tflogidf.txt', 'w')
		maximo = m_tflogidf
		for m in range(0,N):
			print(ciudades[m], paises[m], file=f)
			for i in range(0,top):
				print(str(maximo[m][i][0]) + ' ' + str(maximo[m][i][1]), file=f)

		f = open('tfdoubleidf.txt', 'w')
		maximo = m_tfdoubleidf
		for m in range(0,N):
			print(ciudades[m], paises[m], file=f)
			for i in range(0,top):
				print(str(maximo[m][i][0]) + ' ' + str(maximo[m][i][1]), file=f)


	if sys.argv[1] == '-w2v':
		if len(sys.argv) > 4:
			modelo	= sys.argv[2]
			lista	= sys.argv[3]
			pais	= sys.argv[4]
			sim		= sys.argv[5]
			maximo	= sys.argv[6]
			model	= gensim.models.Word2Vec.load(modelo)
			lista_f = open(lista, 'r')

			palabras = []
			for i in asi_hablamos.gold_standard[pais]:
				if len(i.split()) == 1:
					palabras.append(i.lower())

			r_d = len(palabras)
			print('Total palabras: ' + str(r_d))
			conteo	= 0
			SIM		= int(sim)
			MAX_C	= int(maximo)
			precision = 0

			for linea in lista_f:
				palabra = linea.split()[1]
				if palabra in palabras:
					precision += 1
				conteo +=1
				if conteo > MAX_C:
					break
				similares = model.most_similar(palabra)
				for i in range(0, SIM):
					if similares[i][0] in palabras:
						precision += 1
					conteo +=1
				if conteo > MAX_C:
					break

			print(conteo)
			print('Precision ' + str(precision / r_d))
					

		else:
			print('falta parámetros -w2v MODELO LISTA PAIS')

else:
	print("falta parámetro")
