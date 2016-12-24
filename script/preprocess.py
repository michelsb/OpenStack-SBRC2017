#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv     # imports the csv module
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

types = ["ovs","bridge"]

frame_sizes = ["64","128","256","512","1024","1280","voip","dns","cs"]
applications = ["voip","dns","cs"] 
scenarios = ["1","3","5","7"]
rounds = 100

for typ in types:		

	for scenario in scenarios:

		for frame_size in frame_sizes:

			new_file = open('../results/consolidated/'+typ+'/scenario-'+scenario+'/stats-'+typ+'-'+str(scenario)+'-'+frame_size+'.log', 'wb')
			new_file_writer = csv.writer(new_file, delimiter=' ', quoting=csv.QUOTE_MINIMAL)	

			for step in range(1,rounds+1):

				row = []

				with open('../results/raw/'+typ+'/scenario-'+scenario+'/summary-'+typ+'-'+str(scenario)+'-'+frame_size+'-'+str(step)+'.log') as f:
				    for line in f:    	
				    	elements = line.split()
				    	if len(elements) >= 4:
				    		if elements[0] != '****************':
				    			if elements[1] == 'packets' or elements[0] == 'Minimum' or elements[0] == 'Maximum' or (elements[0] == 'Average' and (elements[1] == 'delay' or elements[1] == 'jitter' or elements[1] == 'bitrate')):
				    				row.append(float(elements[3]))
				    			if elements[2] == 'rate':
				    				row.append(float(elements[4]))
				    			if elements[1] == 'dropped':
				    				row.append(float(elements[4][1:]))    			
				    		else:
				    			break

				new_file_writer.writerow(row)
			
			new_file.close()

