Normalization of BAM files
===========================

## Table of Content

  * [correctGCbias](#correctGCbias)
  * [bamCoverage](#bamCoverage)
  * [bamCompare](#bamCompare)


<a name="correctGCbias"/>
CorrectGCbias
---------------

### What it does (uses output from computeGCbias)
This tool requires the output from computeGCBias to correct the given
BAM files according to the method proposed by Benjamini and Speed
(2012). Nucleic Acids Res.  The resulting BAM files can be used in any
downstream analyses, but be aware that you should not filter out
duplicates from here on.

### output files



<a name="bamCoverage"/>
bamCoverage
------------

### What it does
Given a BAM file, this tool generates a bigWig or bedGraph file of
fragment or read coverages. The way the method works is by first
calculating all the number of reads (either extended to match the
fragment length or not) that overlap each bin in the genome. Bins with
zero counts are skipped, i.e. not added to the output file. The
resulting read counts can be normalized using either a given scaling
factor, the RPKM formula or to get a 1x depth of coverage (RPGC).

### output files



<a name="bamCompare"/>
bamCompare
------------

### What it does

This tool compares two BAM files based on the number of mapped
reads. To compare the BAM files, the genome is partitioned into bins
of equal size, the reads are counted for each bin and each BAM file
and finally, a summarizing value is reported.  This value can be the
ratio of the number of reads per bin, the log2 of the ratio or the
difference.  This tool can normalize the number of reads on each BAM
file using the SES method proposed by [Diaz et al.][]Normalization based on read counts is also
available. The output is either a bedGraph or a bigWig file containing
the bin location and the resulting comparison values.  If paired-end
reads are present, the fragment length reported in the BAM file is
used by default.

  + output files
  + Figure: IGV snapshots of a) BAM,  b) Norm To 1x, c)difference



-----------------------------------------------------------------------------------
[BAM]: https://docs.google.com/document/d/1Iv9QnuRYWCtV_UCi4xoXxEfmSZYQNyYJPNsFHnvv9C0/edit?usp=sharing "binary version of a SAM file; contains all information about aligned reads"
[SAM]: https://docs.google.com/document/d/1Iv9QnuRYWCtV_UCi4xoXxEfmSZYQNyYJPNsFHnvv9C0/edit?usp=sharing "text file containing all information about aligned reads"
[bigWig]: https://docs.google.com/document/d/1Iv9QnuRYWCtV_UCi4xoXxEfmSZYQNyYJPNsFHnvv9C0/edit?usp=sharing "binary version of a bedGraph file; contains genomic intervals and corresponding scores, e.g. average read numbers per 50 bp"
[bedGraph]: https://docs.google.com/document/d/1Iv9QnuRYWCtV_UCi4xoXxEfmSZYQNyYJPNsFHnvv9C0/edit?usp=sharing "text file that contains genomic intervals and corresponding scores, e.g. average read numbers per 50 bp"
[FASTQ]: https://docs.google.com/document/d/1Iv9QnuRYWCtV_UCi4xoXxEfmSZYQNyYJPNsFHnvv9C0/edit?usp=sharing "text file of raw reads (almost straight out of the sequencer)"
### References
[Benjamini and Speed]: http://nar.oxfordjournals.org/content/40/10/e72 "Nucleic Acids Research (2012)"
[Diaz et al.]: http://www.degruyter.com/view/j/sagmb.2012.11.issue-3/1544-6115.1750/1544-6115.1750.xml "Stat. Appl. Gen. Mol. Biol. (2012)"


This tool is developed by the [Bioinformatics Facility](http://www1.ie-freiburg.mpg.de/bioinformaticsfac) at the [Max Planck Institute for Immunobiology and Epigenetics, Freiburg](http://www1.ie-freiburg.mpg.de/).