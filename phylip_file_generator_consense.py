#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  phylip_file_generator_consense.py
#  This script takes a directory with files seperated by split_library_simrlls.py and merge them into a phylip file for phylogeny reconstruction.
#  This script is different from phylip_file_generator.py in the sense that it does the consense among the reads from the same loci and same species first, before concatinating them.
#  Copyright 2016 Huan Fan
#  <hfan22@wisc.edu>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  

import sys, gzip, bz2, os, time
import multiprocessing as mp
from optparse import OptionParser
from functools import reduce
from Bio import AlignIO
from Bio.Align import AlignInfo

def smartopen(filename,*args,**kwargs):
    if filename.endswith('gz'):
        return gzip.open(filename,*args,**kwargs)
    elif filename.endswith('bz2'):
        return bz2.BZ2File(filename,*args,**kwargs)
    else:
        return open(filename,*args,**kwargs)

usage = "usage: %prog [options]"
version = '%prog 20160726.1'
parser = OptionParser(usage = usage, version = version)
parser.add_option("-d", dest = "dataDir", default = 'data',
                  help = "directory containing the data, default = data/")
parser.add_option("-L", dest = "nloci", default = 100, type= int,
                  help = "number of loci to keep, default = 100")
parser.add_option("-r", dest = "read_len", default = 94, type= int,
				  help = "read length, default = 94")

(options, args) = parser.parse_args()

outhandle = file(os.path.basename(options.dataDir.rstrip('/'))+'.phylip', 'w')
read_len = options.read_len
###check the data directory:
if not os.path.isdir(options.dataDir):
    print 'Cannot find data directory {}'.format(options.dataDir)
    sys.exit(2)


###Get sample list:
samples = []
loci_list = {}
for fileName in os.listdir(options.dataDir):
	if os.path.isdir(os.path.join(options.dataDir, fileName)):
		samples.append(fileName)
		loci_list[fileName] = [-1]
	else:
		if not fileName.startswith('.'):
			sample = fileName.split(".")[0]
			if sample in samples:
				sample = fileName.split(".")[0]+fileName.split(".")[1]
				if sample in samples:
					print 'Error, redundant sample or file names. Aborting!'
					sys.exit(3)
			samples.append(sample)
			loci_list[sample] = [-1]
samples.sort()

# Get a dictionary for the number of reads for each locus of each species

for sample in samples:
	filehandle = open(os.path.join(options.dataDir, sample+'.fa'))
	for line in filehandle:
		if line.startswith('>'):
			locus = int(line.split('_')[1].lstrip('locus'))
			loci_list[sample].append(locus)
	filehandle.close()

#Check whether there are loci that are missing in all the samples.
missing = {}
full_list = range(options.nloci)
for sample in samples:
	missing[sample] = set(full_list) - set(loci_list[sample])
missed = reduce(set.intersection,missing.values())
for item in missed:
	full_list.remove(item)

#write the phylip file!
outhandle.write('%d\t%d'%(len(samples),read_len*len(full_list)))
for sample in samples:
	if len(sample) < 10:
		outhandle.write('\n'+sample+' '*(10-len(sample)))
	else:
		outhandle.write(sample[:9]+' ')
	filehandle = open(os.path.join(options.dataDir, sample+'.fa'))
	alignment = {}
	line = filehandle.readline()
	while line:
		if line.startswith('>'):
			locus = int(line.split('_')[1].lstrip('locus'))
			if locus < options.nloci:
				seq = filehandle.readline().rstrip()
				if locus in alignment:
					alignment[locus].append(seq)
				else:
					alignment[locus] = [seq]
		line = filehandle.readline()
	filehandle.close()
	for i in full_list:
		if i in alignment:
			cov = loci_list[sample].count(i)
			if cov > 1:
				phylip = open('temp.phylip','w')
				phylip.write('%d\t%d\n'%(cov,read_len))
				for j in range(cov):
					phylip.write('Sample%d\t%s\n'%(j,alignment[i][j]))
				phylip.close()
				alignments = AlignIO.read(open('temp.phylip'),'phylip-relaxed')
				summary_align = AlignInfo.SummaryInfo(alignments)
				seq = str(summary_align.dumb_consensus())
			elif cov == 1:
				seq = ''.join(alignment[i])
				print(seq)
		else:
			seq = '-'*read_len
		outhandle.write(seq)
outhandle.close()

		


