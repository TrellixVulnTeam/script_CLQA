Summary of scripts
======

### AAAAAAA.*

My stupid way of saving useful snippets of code in various languages. I am an old lady after all.

### aaf\_pairwise_onepair.py
use to be named aaf_pairwise.py. It takes a directory that only contains one pair of samples and calculates the distances between them.

### aaf_phylosim.py
is a variation of aaf_phylokmer.py to process simulated alignments from phylosim.

### aaf\_phylokmer_sba.py
is a variation of aaf_phylokmer.py. It does everything aaf_phylokmer.py does plus generate a sh file containing the kmer_merge command for generating shared-by-all kmers.

### contigtrimmer.py
takes a fasta file and returns only contigs no shorter than the given length

### count2hist.py
takes .pkdat.gz and compute the hist file with the same prefix.

### coverage2region_multi.py
takes a mpileup file and returns the region covered on the reference genome.

### coverage2region_contig.py
this assumes the mpileip file is only from one contig so no dictionary is needed

### extract_sequence.py
takes a genome file and a query (usually a collection of representative sequences of this gene close to this genome) and find the most similar sequence in the genome.

### fastqSpliter.py
takes a fasta file (can be compressed) and output multiple files with one seq_record per file. The file names are the first two words in the seq.description, usually the genus and species name.

### fq\_to\_fa_stdout.pl
is a perl script that takes a fastq file (not compressed) and print to screen the fasta format of it.

### fq\_to_fa.py
is a python script that takes a fastq file (could be compressed) and print to screen the fasta format of it. Use in combinaiton with | gzip >> \*.fa.gz  

### GC_filter.py

filters reads based on a gc range.

### mergeUnmapped.py
In the FlyWolbachia pipeline, I pull unmapped reads from different samples of the same population together for assembly. Before putting all reads in one file, I modifie their tags so it is clear which read is from which sample. This python script generates a shell script that actually does the job.

### ReadsSelector_0407.cpp
This is the script that would compile into ReadsSelector

	g++ ReadsSelector_0407.cpp -o ReadsSelector2
	mv ReadsSelector2 /usr/local/bin/

### seq_qual2trimmed_fastq.py
This combines trimFastq4mothur.py and fasta_to_fastq.py

### seq_stats.py
is used to calculate the total, mean, and variance of seq lengths in a seq file.

### singletonCalculator.py
takes shared kmer table (comparing to whole kmer table where kmers shared only by one species is included.

### singletonsInPkdat.py
takes .pkdat file generated by kmer_count(x) and counts the number of kmers with a frequency of 1. To be distinguished from singletonCalculator.py.

### subsample\_kmer_v2.py
Some times we face a dataset with more than 1 order of magnitude differences in their counted kmer file. If the kmers were counted from genome assembly, there's nothing we could do about it. If the kmers were counted from raw data, especially metagenomic data, there is risk of insufficient sampling effort. A common practice in metagenomic analysis is to subsample other samples to the lowest acceptable sample and this script does it WITHOUT replacement in order to keep the same kmer diversity afterwards.  

### trimFastq4mothur.py
takes sanger sequencing reads and trim it based on quality score. If it is still longer than 1000bp after trimming, it will be trimmed from the end to make it shorter than 1000bp so mothur would take it for its makecontigs function.

### trim_primer.py
takes read files and trim the primer sequences from the beginning of the reads. Returns another file with '\_cut' to the end of the filename (.suffix excluded). Takes gzipped files as well. The output format matches the input.

### x2y.pl
Universal converter of various formats in bioinformatics. See a detailed list at [Bio::SeqIO](http://bioperl.org/howtos/SeqIO_HOWTO.html).
