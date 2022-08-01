import os,argparse, time
from Bio import SeqIO


def get_seq(infile,file_type):
    seq = ''
    for record in SeqIO.parse(infile, file_type):
        seq = 'N'.join(seq, record.seq)
    return(seq)

def run_command(command):
    print(command)
    print(time.strftime('%c'))
    try:
        os.system(command)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="subset a file by a list")
    parser.add_argument("-i", "--input", required=True, type=str, help="input seq file")
    parser.add_argument("-o", "--output", required=True, type=str, help="output kmer count file")
    parser.add_argument("-k", "--k_len", required=True, type=int, help="kmer size")
    parser.add_argument("-s", "--skip", required=True, type=int, help="column number of in big file")
    parser.add_argument("-f", "--file_type", required=True, type=str,
        default='fasta', help="field delimiter, default is tab")

    Args = parser.parse_args()
    kmerCount = './kmer_count_rz'
    if not is_exe(kmerCount):
        print('kmer_count_rz not found. Make sure it is in your PATH or the')
        print('current directory, and that it is executable')
        sys.exit(1)
    seq = get_seq(Args.input, Args.file_type)
    command = ' '.join([kmerCount, '-i', seq, '-n', Args.k_len, '-s', Args.skip,
    '>', Args.output])
    run_command(command)
