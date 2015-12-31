#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  split_libraries_fastq_FH.py
#
#  This script is written for Laura Ladwig's metagenomic data. She had miseq data of fungi (ITS) and bacteria(*S) from 88 samples. The data come in one file. Now I need to seperate them into 88 separate ones, which is usually called multiperplexing in metagenomic world.
#  
#  Copyright 2015 Huan Fan <hfan22@wisc.edu>
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

import sys, gzip, bz2, os, time, math, re
import multiprocessing as mp
from optparse import OptionParser

def smartopen(filename,*args,**kwargs):
	'''opens with open unless file ends in .gz, then use gzip.open
		in theory should transparently allow reading of files regardless of
		compression'''
	if filename.endswith('gz'):
		return gzip.open(filename,*args,**kwargs)
	elif filename.endswith('bz2'):
		return bz2.BZ2File(filename,*args,**kwargs)
	else:
		return open(filename,*args,**kwargs)

def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def countShared(lines, sn): #count nshare only, for shared kmer table
	shared = [[0] * sn for i in xrange(sn)]
	for line in lines:
		line = line.split()
		if len(line) == sn+1:
			line = line[1:]
		line = [int(i) for i in line]
		for i in xrange(sn):
			for j in xrange(i + 1, sn):
				if line[i] > 0 and line[j] > 0:
					shared[i][j] += 1
	return shared

usage = "usage: %prog [options]"
version = '%prog 20151230.1'
parser = OptionParser(usage = usage, version = version)
parser.add_option("-i", dest = "index",
                  help = "the index file in fastq format")
parser.add_option("--R1", dest = "R1",
                  help = "pair-end file 1")
parser.add_option("--R2", dest = "R2",
                  help = "pair-end file 2")

(options, args) = parser.parse_args()
    
index_handle = file(options.index)
R1_handle =  file(options.R1)
R2_handle =  file(options.R2)

###check the input files:
if not os.path.exists(options.index):
    print 'Cannot find index file {}'.format(options.index)
    sys.exit(2)

if not os.path.exists(options.R1):
    print 'Cannot find pair-end file 1 {}'.format(options.R1)
    sys.exit(2)

if not os.path.exists(options.R2):
    print 'Cannot find pair-end file 1 {}'.format(options.R2)
    sys.exit(2)

# read in the code files
bacteria={}
fungi={}
index={}
bacteria_filehandle=file('bacteria_withSampleCode.txt')
fungi_filehandle=file('fungi_withSampleCode.txt')
for line in bacteria_filehandle:
    if line.startswith('#'):
        continue
    else:
        bacteria[line.split()[1]]=line.split()[-1]
for line in fungi_filehandle:
    if line.startswith('#'):
        continue
    else:
        fungi[line.split()[1]]=line.split()[-1]

from Bio import SeqIO
for seq_record in SeqIO.parse(index_handle,"fastq"):
    if seq_record.seq in bacteria:
        index[seq_record.id]= 'bac_'+bacteria[seq_record.seq]
    else if seq_record.seq in fungi:
        index[seq_record.id]= 'fun_'+fungi[seq_record.seq]

for key in bacteria:
    files['bac_'+key] = open('bac_%key.fq' %key, 'w')
for key in fungi:
    files['fun_'+key] = open('fun_%key.fq' %key, 'w')

from itertools import izip
for line1, line2 in izip(open('R1.fq'),open('R2.fq')):
    if line1.startswith('@'):
        files[index[line1.rstrip()]]


    

#Get sample list and split alignment file into seperate fasta files for each node:
dir_name = options.phyloSimFile.split('.')[0]
os.system('mkdir {}'.format(dir_name))
samples = []
input=open(options.phyloSimFile)
from Bio import SeqIO
for seq_record in SeqIO.parse(input,"fasta"):
	if seq_record.id != "Node":
		samples.append(seq_record.id)
		fh=open(dir_name+"/"+seq_record.id+".temp.fa","w")
		fh.write(">"+seq_record.id+"\n")
		seq_record.seq = re.sub("-","",str(seq_record.seq))
		fh.write(str(seq_record.seq))
		fh.close()
input.close()
samples.sort()

print 'SPECIES LIST:'
for sample in samples:
    print sample
print time.strftime('%c'),"counting kmers"
#Prepare kmer_count jobs. Here we use single core since the other cores will be used for parallele simulation
jobList = []
for sample in samples:
	outFile = '{}/{}.pkdat'.format(dir_name,sample)
	command = '{} -l {} -G {} -o {}'.format(kmerCount, kl,
											options.memSize, outFile)
	if os.path.exists(dir_name+"/"+sample+".temp.fa"):
		command += ' -i {}/{}.temp.fa'.format(dir_name, sample)
	else:
		print 'Error, file {}/{}.temp.fa does not exist. Aborting!'.\
                   format(dir_name, sample)
		sys.exit(3)
	command += ' > {}/{}.wc'.format(dir_name,sample)
	jobList.append(command)
jobList = jobList[::-1]

#Run jobs (1 thread)
for job in jobList:
	print job
	os.system(job)


#Merge output wc files
divFile = os.path.join(dir_name, 'kmer_diversity.wc')
handle = open(divFile, 'w')
for sample in samples:
	kmerFile = dir_name + "/" + sample + '.wc'
	fh = open(kmerFile)
	kmerNum = fh.readline().split(":")[1]
	handle.write(sample + ":" + kmerNum)
	fh.close()
	os.remove(kmerFile)
handle.close()

#Run kmer_merge
outFile = os.path.join(dir_name, options.outFile)
command = "{} -k s -c -d '0' -a 'T,M,F'".format(filt)
cut = []
if options.withKmer:
	cut.append('1')
for i, sample in enumerate(samples):
    command += ' {}.pkdat'.format(os.path.join(dir_name, sample))
    cut.append(str((i + 1) * 2))
if options.outFile.endswith('.gz'):
    command += ' | cut -f {} | gzip > {}'.format(','.join(cut), outFile)
else:
    command += ' | cut -f {} > {}'.format(','.join(cut), outFile)
print '\n', time.strftime('%c'), "generating shared kmer table"
print command
os.system(command)
print time.strftime('%c'), 'Compute the distance matrix'

###aaf_distance.py
os.chdir("./{}".format(dir_name))
#Check input files
try:
	total = open("kmer_diversity.wc")
except IOError:
	print 'Cannot open file {}/kmerdiversity.wc'.format(dir_name)
	sys.exit()

#Check output files
try:
	nsnt = file(dir_name+'_nshare.csv','w')
except IOError:
	print 'Cannot open',dir_name+'_nshare.csv', 'for writing'
	sys.exit()


#Compute shared kmer matrix
sn = len(samples)    #species number
handle = smartopen(options.outFile)
lines = handle.readlines()
nshare = countShared(lines, sn)
handle.close()

#Compute distance matrix
ntotal = [0.0] * sn

for i in xrange(sn):
	ntotal[i] = float(total.readline().split()[1])
	if i < sn - 1:
		nsnt.write('%s%s' % (samples[i], ',')) # First line for the nshare csv file
	else:
		nsnt.write('%s\n' % samples[i]) #no extra comma at the end of the line

dist = [[0] * sn for i in xrange(sn)]

for i in xrange(sn):
	for j in xrange(i + 1, sn):
		mintotal = min(ntotal[i], ntotal[j])
		if nshare[i][j] == 0:
			dist[j][i] = dist[i][j] = 1
		else:
			distance = (-1 / kl) * math.log(nshare[i][j] / mintotal)
			dist[j][i] = dist[i][j] = distance
			nshare[j][i] = nshare[i][j]

total.close()

#Write infile
try:
	infile = open('infile','w')
except IOError:
	print 'Cannot open infile for writing'
	sys.exit()

infile.write('{} {}'.format(sn, sn))
namedic = {}
for i in xrange(sn):
	lsl = len(samples[i])
	if lsl >= 10:
		ssl = samples[i][:10]
		appendix = 1
		while ssl in namedic:
			ssl = samples[i][:9]+str(appendix)
			appendix += 1
	else:
		ssl = samples[i] + ' ' * (10 - lsl)
	namedic[ssl] = samples[i]
	infile.write('\n{}'.format(ssl))
	for j in xrange(sn):
		infile.write('\t{}'.format(dist[i][j]))
		if i==j:
			if j == sn - 1:
				nsnt.write('{}\n'.format(ntotal[i]))
			else:
				nsnt.write('%s%s' % (ntotal[i], ','))
		else:
			if j == sn - 1:
				nsnt.write('{}\n'.format(nshare[i][j]))
			else:
				nsnt.write('%s%s' % (nshare[i][j], ','))

infile.close()
nsnt.close()

###Run fitch_kmer
print time.strftime("%c"), 'building tree'
if os.path.exists("./outfile"):
	os.system("rm -f outfile outtree")
command = 'printf "K\n{}\nY" | {} > /dev/null'.format(int(kl),fitch)
os.system(command)
fh = open('outtree')
fh1 = open(dir_name+'.tre','w')

for line in fh:
	for key in namedic:
		if key.rstrip()+":" in line:
			newline = line.replace(key,namedic[key].rstrip(),1)
			line = newline
	fh1.write(newline)
fh.close()
fh1.close()
fh = open('infile')
fh1 = open(dir_name+'.dist','w')
for line in fh:
	for key in namedic:
		if line.startswith(key):
			newline = line.replace(key,namedic[key],1)
			line = newline
			break
	fh1.write(newline)


fh.close()
fh1.close()
os.system('rm -f outfile infile outtree')

print time.strftime("%c"), 'end'

