#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  split_libraries_fastq_FH.py
#
#  This script is written for spliting simrlls simulation data. This also includes 1) getting rid of barcode 2) introduce random dropout rate
#  
#  Copyright 2016 Huan Fan <hfan22@wisc.edu>
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

import sys, gzip, bz2, os, time, math, re, argparse,random
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



usage = "usage: %prog [options]"
version = '%prog 20160211.1'
parser = OptionParser(usage = usage, version = version)
parser.add_option("-i", dest = "input",
                  help = "fastq file simulated from simrlls")
parser.add_option("-r", dest = "rate", type = float, default = 0,
                  help = "dropout rate")
parser.add_option("-d", dest = "dir", default = "simrlls",
                  help = "output directory for fasta files after seperation")

(options, args) = parser.parse_args()

input_handle = smartopen(options.input)
rate = options.rate
outputDir = options.dir

###check user input:
if not os.path.exists(options.input):
    print('Cannot find input file {}'.format(options.input))
    sys.exit(2)

if os.path.exists(outputDir):
    print('The output directory {} already exist'.format(options.dir))
    sys.exit(2)
else:
    os.system('mkdir {}'.format(outputDir))

### Start processing input file
from Bio import SeqIO
samples = {} # {sample name: sample output file handle}

for seq_record in SeqIO.parse(input_handle,"fastq"):
    if rate < random.random():
        sample = seq_record.id.split('_')[2]
        if sample in samples:
            samples[sample].write('>'+seq_record.id+'\n')
            samples[sample].write(str(seq_record.seq[6:])+'\n')
        else:
            samples[sample] = open(outputDir+'/'+sample+'.fa','w')

for key in samples:
    samples[key].close()

input_handle.close()