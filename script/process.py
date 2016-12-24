#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv     # imports the csv module
import rpy2.robjects as robjects
import matplotlib.pyplot as plt
import numpy as np
import sys 
import os 

reload(sys)  
sys.setdefaultencoding('utf8')

types = ["ovs","bridge"]

#frame_sizes = ["64","128","256","512","1024","1280","voip","dns","cs"]
frame_sizes = ["64","128","1024","1280"]
#frame_sizes = ["1024","1280"]
applications = ["voip","dns","cs"] 
scenarios = ["1","3","5","7"]
#scenarios = ["5","7"]

confidence_interval = 0.05	

# 0 - Total Packets
# 1 - Minimum delay (s)
# 2 - Maximum delay (s)
# 3 - Average delay (s)
# 4 - Average jitter (s)
# 5 - Average packet rate (kbps)
# 6 - Average bitrate (pps)
# 7 - Packets dropped rate (%)

#metrics = ["bandwidth-pps","bandwidth-kbps","latency","jitter","packet-loss"]
#metrics_position = {"bandwidth-pps":6,"bandwidth-kbps":5,"latency":3,"jitter":4,"packet-loss":7}
#metrics_title = {"bandwidth-pps":"Taxa de Transmissão (pps)","bandwidth-kbps":"Taxa de Transmissão (Kbps)","latency":"Latência (milissegundos)","jitter":"Jitter (milissegundos)","packet-loss":"Taxa de Perda de Pacotes (%)"}

metrics = ["bandwidth-mbps","latency","jitter","packet-loss"]
metrics_position = {"bandwidth-mbps":5,"latency":3,"jitter":4,"packet-loss":7}
metrics_title = {"bandwidth-mbps":"Taxa de Transmissão (Mbps)","latency":"Latência (Milissegundos)","jitter":"Jitter (Milissegundos)","packet-loss":"Taxa de Perda de Pacotes (%)"}

#metrics = ["bandwidth-pps","bandwidth-kbps","latency","jitter"]
#metrics_position = {"bandwidth-pps":6,"bandwidth-kbps":5,"latency":3,"jitter":4}
#metrics_title = {"bandwidth-pps":"Taxa de Transmissão (pps)","bandwidth-kbps":"Taxa de Transmissão (Kbps)","latency":"Latência (milissegundos)","jitter":"Jitter (milissegundos)"}


os.system("rm -rf ../figures ../norm-tests ../np-tests")

os.system("mkdir -p ../np-tests/datagram")
os.system("mkdir -p ../np-tests/scenario")

for scenario in scenarios:
	for metric in metrics:
		os.system("mkdir -p ../figures/eda/scenario-"+scenario+"/"+metric)		
		os.system("mkdir -p ../norm-tests/scenario-"+scenario+"/"+metric)

for metric in metrics:
	os.system("mkdir -p ../figures/datagram/"+metric)
	os.system("mkdir -p ../figures/scenario/"+metric)

r = robjects.r
r.library("nortest")
r.library("MASS")

r('''
        wilcox.onesample.test <- function(v, verbose=FALSE) {
           wilcox.test(v,mu=median(v),conf.int=TRUE, conf.level = 0.95)
        }
        wilcox.twosamples.test <- function(v, r, verbose=FALSE) {
           wilcox.test(v,r)
        }        
        ''')

# Normality Test
lillie = robjects.r('lillie.test') # Lilliefors

# Close pdf graphics
close_pdf = robjects.r('dev.off') 

# Non-parametric Tes
wilcoxon_test_two_samples = robjects.r['wilcox.twosamples.test']
wilcoxon_test_one_sample = robjects.r['wilcox.onesample.test']

result_norm_test = open('../norm-tests/result-norm-test.csv', 'wb') # opens the csv file
result_norm_test_writer = csv.writer(result_norm_test, delimiter=' ', quoting=csv.QUOTE_MINIMAL)	
result_norm_test_writer.writerow(['PDS','Cenário', 'Tipo de Datagrama', 'Métrica', 'P-Value'])

vector_samples = dict()

for typ in types:	

	if typ == "ovs":
		title = "OpenVSwitch "
	else:
		title = "Linux Bridge "

	vector_samples[typ] = dict()

	for scenario in scenarios:
		
		vector_samples[typ][scenario] = dict()

		for frame_size in frame_sizes:

			vector_samples[typ][scenario][frame_size] = dict()

			f = open('../results/consolidated/'+typ+'/scenario-'+scenario+'/stats-'+typ+'-'+str(scenario)+'-'+frame_size+'.log', 'rb') # opens the csv file
			
			try:
		 	    array_metric = dict()
		 	    for metric in metrics:
		 	        	vector_samples[typ][scenario][frame_size][metric]=dict()
		 	        	array_metric[metric]=[]
		 	    reader = csv.reader(f,delimiter=' ') #creates the reader object
		 	    for row in reader:   # iterates the rows of the file in orders		    	
		 	        tester = False
		 	        for metric in metrics:
		 	        	value = float(row[metrics_position[metric]])
		 	        	if value < 0.0:
			 	        	tester = True
					if tester:
						break
		 	        for metric in metrics:		 	        	
			 	        value = float(row[metrics_position[metric]])
			 	        if metric == "latency" or metric == "jitter":
			 	        	array_metric[metric].append(value*1000)
			 	        elif metric == "bandwidth-mbps":
			 	        	array_metric[metric].append(value/1000)
			 	        else: 
			 	        	array_metric[metric].append(value)
		 	finally:
		 	    f.close()     

		 	# Análsie Exploratória de Dados

		 	if frame_size in applications:
 				title_graph = title + " - Aplicação: " + frame_size + " - "+scenario+" VNF(s)"
 			else:
 				title_graph = title + " - Tamanho (bytes): " + frame_size + " - "+scenario+" VNF(s)"

		 	for metric in metrics:
				
				vector_samples[typ][scenario][frame_size][metric]["sample"] = robjects.FloatVector(array_metric[metric])
 		 	 	vector_samples[typ][scenario][frame_size][metric]["median"] = r.median(vector_samples[typ][scenario][frame_size][metric]["sample"])[0]
 		 	 	vector_samples[typ][scenario][frame_size][metric]["mean"] = r.mean(vector_samples[typ][scenario][frame_size][metric]["sample"])
 		 	 	vector_samples[typ][scenario][frame_size][metric]["sd"] = r.sd(vector_samples[typ][scenario][frame_size][metric]["sample"])
 		 	 	vector_samples[typ][scenario][frame_size][metric]["max"] = r.max(vector_samples[typ][scenario][frame_size][metric]["sample"])[0]
 		 	 	vector_samples[typ][scenario][frame_size][metric]["min"] = r.min(vector_samples[typ][scenario][frame_size][metric]["sample"])[0]

 		 	 	if vector_samples[typ][scenario][frame_size][metric]["median"] != 0:

	 		 	 	xlabel = metrics_title[metric]

					# Histograma
					r.pdf("../figures/eda/scenario-"+scenario+"/"+metric+"/hist-"+metric+"-"+typ+"-"+str(scenario)+"-"+frame_size+".pdf")
	 				r.hist(vector_samples[typ][scenario][frame_size][metric]["sample"], main = title_graph, col="blue", xlab = xlabel, ylab = "Frequência Absoluta")
	 				close_pdf()
	 				# Boxplots
	 				r.pdf("../figures/eda/scenario-"+scenario+"/"+metric+"/box-"+metric+"-"+typ+"-"+str(scenario)+"-"+frame_size+".pdf")
	 				r.boxplot(vector_samples[typ][scenario][frame_size][metric]["sample"], main = title_graph,col="lightblue", horizontal=True, las=1, xlab=xlabel)
	 				close_pdf()
					# Grafico de probabilidade (QQ)
	 				r.pdf("../figures/eda/scenario-"+scenario+"/"+metric+"/qq-"+metric+"-"+typ+"-"+str(scenario)+"-"+frame_size+".pdf")
	 				r.qqnorm(vector_samples[typ][scenario][frame_size][metric]["sample"], main = title_graph, xlab = "Quantis teóricos N(0,1)", pch = 20,
	 		 		ylab = xlabel)
	 				r.qqline(vector_samples[typ][scenario][frame_size][metric]["sample"], lty = 2, col = "red")
	 				close_pdf()

					filename_norm_tests = '../norm-tests/scenario-'+scenario+'/'+metric+'/norm-tests-'+metric+'-'+typ+'-'+str(scenario)+'-'+frame_size+'.csv'
					norm_tests = open(filename_norm_tests, 'wb') # opens the csv file		
						
					tester = False
					methods= ""
					#p_values= ""
					#count=0

			 	 	try:			
			 	 		norm_tests_writer = csv.writer(norm_tests, delimiter=' ', quoting=csv.QUOTE_MINIMAL)			
			 	 		norm_tests_writer.writerow(['Method', 'Statistic', 'P-Value','Alternative Hypothesis (KS Test)'])		 
			 	 		
			 	 		test = lillie(vector_samples[typ][scenario][frame_size][metric]["sample"])
			 	 		norm_tests_writer.writerow([test[2][0], test[0][0],test[1][0],''])		 	 		
			 	 		if (float(test[1][0]) >= confidence_interval):
			 	 			tester=True
			 	 			#methods = methods + "," + test[2][0]
			 	 			#p_values = str(test[1][0])
			 	 			#count+=1		 	 		
			 	 		
			 	 		p_value = "{:.2e}".format(test[1][0])

			 	 		if tester: 
			 	 			result_norm_test_writer.writerow([typ,scenario,frame_size,metric,p_value])
			 	 			#vector_samples[typ][scenario][frame_size][metric]["normtest"] = "*"+str(p_value)
			 	 		#else:
			 	 			#vector_samples[typ][scenario][frame_size][metric]["normtest"] = str(p_value)

					finally:
			 	 	    norm_tests.close()		 	 			
					
					test_wilcoxon = wilcoxon_test_one_sample(vector_samples[typ][scenario][frame_size][metric]["sample"])							
					error_max = test_wilcoxon[7][1]		
					median = test_wilcoxon[8][0]

					vector_samples[typ][scenario][frame_size][metric]["wilcoxon_test_median"] = median
					vector_samples[typ][scenario][frame_size][metric]["wilcoxon_test_error"] = float(error_max)-float(median)

result_norm_test.close()

x = np.arange(len(scenarios))

filename_np_metrics = dict()
writer_np_metrics = dict()
vectors_median = dict()

fig_num=0

# Usando a quantidade de VNFs como eixo X (uma figura por frame size)

for metric in metrics[:-1]:	
	
	filename_np_metrics[metric] = open('../np-tests/'+metric+'-np-test.csv', 'wb') # opens the csv file
	writer_np_metrics[metric] = csv.writer(filename_np_metrics[metric], delimiter=' ', quoting=csv.QUOTE_MINIMAL)	
	writer_np_metrics[metric].writerow(['Tipo Datagrama','Cenário 1', 'Cenário 3', 'Cenário 5', 'Cenário 7'])

	ylabel = metrics_title[metric]		
	for frame_size in frame_sizes:			
		csv_np_row = [frame_size]
		np_tests_per_frame = open('../np-tests/np-tests-wilcoxon-'+metric+'-'+frame_size+'.csv', 'wb')	
		np_tests_per_frame_writer = csv.writer(np_tests_per_frame, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
		np_tests_per_frame_writer.writerow(['Scenario', 'Statistic', 'P-Value','Alternative Hypothesis'])
		vectors_median["ovs"] = []
		vectors_median["ovs-errors"] = []
		vectors_median["bridge"] = []
		vectors_median["bridge-errors"] = []
		for scenario in scenarios:							
			np_test = wilcoxon_test_two_samples(vector_samples["bridge"][scenario][frame_size][metric]["sample"],vector_samples["ovs"][scenario][frame_size][metric]["sample"])
			np_tests_per_frame_writer.writerow([scenario, np_test[0][0],np_test[2][0],np_test[4][0]])
			p_value = "{:.2e}".format(np_test[2][0])
			if (float(np_test[2][0]) >= confidence_interval):
				csv_np_row.append(str(p_value)) 
			else:
				csv_np_row.append("*"+str(p_value)) 			
			vectors_median["ovs"].append(vector_samples["ovs"][scenario][frame_size][metric]["wilcoxon_test_median"])
			vectors_median["ovs-errors"].append(vector_samples["ovs"][scenario][frame_size][metric]["wilcoxon_test_error"])
			vectors_median["bridge"].append(vector_samples["bridge"][scenario][frame_size][metric]["wilcoxon_test_median"])	
			vectors_median["bridge-errors"].append(vector_samples["bridge"][scenario][frame_size][metric]["wilcoxon_test_error"])		
		np_tests_per_frame.close()		
		
		writer_np_metrics[metric].writerow(csv_np_row)

		if frame_size in applications:
				title_graph = "Aplicação: " + frame_size.upper()
		else:
				title_graph = "Tamanho do Datagrama (bytes): " + frame_size
		fig_num = fig_num + 1
		plt.figure(fig_num)
		width = 0.35       # the width of the bars	
		opacity = 0.5
		error_config = {'ecolor': 'black'}
		
		fig, ax = plt.subplots()
		rects1 = ax.bar(x, vectors_median["ovs"], width, alpha=opacity, color='m',yerr=vectors_median["ovs-errors"],error_kw=error_config) #yerr=menStd
		rects2 = ax.bar(x + width, vectors_median["bridge"], width, alpha=opacity, color='c',yerr=vectors_median["bridge-errors"],error_kw=error_config)
		# add some text for labels, title and axes ticks
		ax.set_ylabel(ylabel)
		ax.set_xlabel("Quantidade de VNFs")
		ax.set_title("")
		ax.set_xticks(x + width)
		ax.set_xticklabels(scenarios)
		ax.legend((rects1[0], rects2[0]), ('OpenVSwitch', 'Linux Bridge'),bbox_to_anchor=(0., 1.02, 1., .102), loc=3,ncol=2, mode="expand", borderaxespad=0.)
		plt.savefig("../figures/scenario/"+metric+"/median-"+frame_size+"-"+metric+".pdf",format='pdf')	

	filename_np_metrics[metric].close()

x = np.arange(2)

vectors_median = dict()

#frame_sizes = ["64","128","1024","1280"]

for metric in metrics:
	ylabel = metrics_title[metric]
	xlabel="Tamanho do Datagrama (Bytes)"
	for scenario in scenarios:
		vectors_median["ovs"] = []
		vectors_median["ovs-errors"] = []
		vectors_median["bridge"] = []
		vectors_median["bridge-errors"] = []
		for frame_size in frame_sizes:			
			if vector_samples["ovs"][scenario][frame_size][metric]["median"] != 0:
				vectors_median["ovs"].append(vector_samples["ovs"][scenario][frame_size][metric]["wilcoxon_test_median"])
				vectors_median["ovs-errors"].append(vector_samples["ovs"][scenario][frame_size][metric]["wilcoxon_test_error"])
			else:
				vectors_median["ovs"].append(0)
				vectors_median["ovs-errors"].append(0)
			if vector_samples["bridge"][scenario][frame_size][metric]["median"] != 0:	
				vectors_median["bridge"].append(vector_samples["bridge"][scenario][frame_size][metric]["wilcoxon_test_median"])	
				vectors_median["bridge-errors"].append(vector_samples["bridge"][scenario][frame_size][metric]["wilcoxon_test_error"])
			else:				
				vectors_median["bridge"].append(0)	
				vectors_median["bridge-errors"].append(0)
		title_graph = "Tamanho do Datagrama (bytes): " + frame_size
		fig_num = fig_num + 1
		plt.figure(fig_num)
		width = 0.35       # the width of the bars	
		opacity = 0.5
		error_config = {'ecolor': 'black'}

		def autolabel(bx, rects):
		    for rect in rects:
		        height = rect.get_height()
		        bx.text(rect.get_x() + rect.get_width()/2., .95*height,
		                '%d' % int(height),
		                ha='center', va='bottom')

		if metric != "packet-loss":

			fig, (ax1, ax2) = plt.subplots(1,2, sharex=False, sharey=False)

			rects11 = ax1.bar(x, vectors_median["ovs"][0:2], width, alpha=opacity, color='m',yerr=vectors_median["ovs-errors"][0:2],error_kw=error_config) #yerr=menStd
			rects12 = ax1.bar(x + width, vectors_median["bridge"][0:2], width, alpha=opacity, color='c',yerr=vectors_median["bridge-errors"][0:2],error_kw=error_config)
			ax1.set_title("")
			ax1.set_xticks(x + width)
			ax1.set_xticklabels(frame_sizes[0:2],fontsize=14)
			#ax1.get_yticks().set_fontsize(14)
			ax1.grid(True)

			rects21 = ax2.bar(x, vectors_median["ovs"][2:4], width, alpha=opacity, color='m',yerr=vectors_median["ovs-errors"][2:4],error_kw=error_config) #yerr=menStd
			rects22 = ax2.bar(x + width, vectors_median["bridge"][2:4], width, alpha=opacity, color='c',yerr=vectors_median["bridge-errors"][2:4],error_kw=error_config)
			ax2.set_title("")
			ax2.set_xticks(x + width)
			ax2.set_xticklabels(frame_sizes[2:4],fontsize=14)
			#ax2.legend((rects21[0], rects22[0]), ('OVS', 'LB'),bbox_to_anchor=(0., 1.02, 1., .102), loc=3,ncol=2, mode="expand", borderaxespad=0.)
			#ax2.get_yticks().set_fontsize(14)
			ax2.grid(True)		

			#autolabel(ax1,rects11)
			#autolabel(ax1,rects12)
			#autolabel(ax2,rects21)
			#autolabel(ax2,rects22)

			plt.legend((rects21[0], rects22[0]), ('Open vSwitch', 'Linux Bridge'), bbox_to_anchor=(-1.1, 1.04, 1.8, .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

		else:

			fig, ax1 = plt.subplots()

			rects21 = ax1.bar(x, vectors_median["ovs"][2:4], width, alpha=opacity, color='m',yerr=vectors_median["ovs-errors"][2:4],error_kw=error_config) #yerr=menStd
			rects22 = ax1.bar(x + width, vectors_median["bridge"][2:4], width, alpha=opacity, color='c',yerr=vectors_median["bridge-errors"][2:4],error_kw=error_config)
			ax1.set_title("")
			ax1.set_xticks(x + width)
			ax1.set_xticklabels(frame_sizes[2:4],fontsize=14)
			#ax1.legend((rects21[0], rects22[0]), ('OVS', 'LB'),bbox_to_anchor=(0., 1.02, 1., .102), loc=3,ncol=2, mode="expand", borderaxespad=0.)
			ax1.grid(True)		

			plt.legend((rects21[0], rects22[0]), ('Open vSwitch', 'Linux Bridge'), bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

			#autolabel(ax1,rects21)
			#autolabel(ax1,rects22)		

		fig.text(0.5, 0.02, xlabel, ha='center', fontsize=16)
		fig.text(0.03, 0.5, ylabel, va='center', rotation='vertical', fontsize=16)
		
		#bbox_to_anchor=(0., 1.02 (heigth), 1. (width), .102)

		#plt.legend((rects21[0], rects22[0]), ('Open vSwitch', 'Linux Bridge'), bbox_to_anchor=(-1.1, 1.04, 1.8, .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
		plt.tick_params(labelsize=14)
		plt.subplots_adjust(wspace = .3)
		plt.savefig("../figures/datagram/"+metric+"/median-"+scenario+"-"+metric+".pdf",format='pdf')

		 	# print typ + "-------" + scenario + " ----- " + frame_size

		 	# for metric in metrics:
		 	# 	print ">>>>>>>>>" + metric + "<<<<<<<<<<<"
		 	# 	print array_metric[metric]
		 	# print "---------------------------------------------------"
		 	# print
		 	# print
		


