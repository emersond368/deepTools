#!/usr/bin/env python
#-*- coding: utf-8 -*-

import argparse
import sys
import os
import os.path
import shutil

from deeptools.parserCommon import writableFile, numberOfProcessors
from deeptools import heatmapper
from deeptools._version import __version__
import deeptools.config as cfg
import deeptools.utilities

def parse_arguments(args=None):
    parser = \
        argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="""

This tool summarizes and prepares an intermediary file containing
scores associated with genomic regions that can be used afterwards to
plot a heatmap or a profile.  Typically, these genoic regions are
genes, but any other regions defined in a BED format can be
used. This tool can also be used to filter and sort regions according
to their score.

To learn more about the specific parameters type:

%(prog)s reference-point --help or
%(prog)s scale-regions --help

""",
            epilog='An example usage is:\n  %(prog)s reference-point -S '
            '<biwig file> -R <bed file> -b 1000\n \n')

    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))

    subparsers = parser.add_subparsers(
        title='Commands',
        dest='command',
        metavar='')

    # scale-regions mode options
    scaleRegions = subparsers.add_parser(
        'scale-regions',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[computeMatrixRequiredArgs(),
                 computeMatrixOutputArgs(),
                 computeMatrixOptArgs(case='scale-regions')],
        help="In the scale-regions mode, all regions in the BED file are "
        "stretched or shrunk to the same length (bp) that is indicated by "
        "the user.",
        usage='An example usage is:\n  computeMatrix -S '
        '<biwig file> -R <bed file> -b 1000\n \n')


    # reference point arguments
    refpoint = subparsers.add_parser(
        'reference-point',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[computeMatrixRequiredArgs(),
                 computeMatrixOutputArgs(),
                 computeMatrixOptArgs(case='reference-point')],
        help="Reference-point refers to a position within a BED region "
        "(e.g., the start of region). In this mode only those genomic"
        "positions before (upstream) and/or after (downstream) of the "
        "reference point will be plotted.",
        usage='An example usage is:\n  computeMatrix -S '
        '<biwig file> -R <bed file> -a 3000 -b 3000\n\ n')

    return parser


def computeMatrixRequiredArgs(args=None):
    parser = argparse.ArgumentParser(add_help=False)
    required = parser.add_argument_group('Required arguments')
    required.add_argument('--regionsFileName', '-R',
                          metavar='File',
                          help='File name, in BED format, containing '
                               'the regions to plot. If multiple bed files are given, each one is considered a '
                               'group that can be plotted separately. Also, adding a "#" symbol in the bed file '
                               'causes all the regions until the previous "#" to be considered one group.',
                          type=argparse.FileType('U'),
                          nargs='+',
                          required=True)
    required.add_argument('--scoreFileName', '-S',
                          help='bigWig file(s) containing '
                          'the scores to be plotted. BigWig '
                          'files can be obtained by using the bamCoverage '
                          'or bamCompare tools. More information about '
                          'the bigWig file format can be found at '
                          'http://genome.ucsc.edu/goldenPath/help/bigWig.html ',
                          metavar='File',
                          nargs='+',
                          type=argparse.FileType('r'),
                          required=True)
    return parser


def computeMatrixOutputArgs(args=None):
    parser = argparse.ArgumentParser(add_help=False)
    output = parser.add_argument_group('Output options')
    output.add_argument('--outFileName', '-out',
                        help='File name to save the gzipped matrix file '
                        'needed by the "heatmapper" and "profiler" tools.',
                        type=writableFile,
                        required=True)
    #TODO This isn't implemented, see deeptools/heatmapper.py in the saveTabulatedValues() function
    #output.add_argument('--outFileNameData',
    #                    help='Name to save the averages per matrix '
    #                    'column into a text file. This corresponds to '
    #                    'the underlying data used to '
    #                    'plot a summary profile. Example: myProfile.tab',
    #                    type=argparse.FileType('w'))

    output.add_argument('--outFileNameMatrix',
                        help='If this option is given, then the matrix '
                        'of values underlying the heatmap will be saved '
                        'using the indicated name, e.g. IndividualValues.tab.'
                        'This matrix can easily be loaded into R or '
                        'other programs.',
                        metavar='FILE',
                        type=writableFile)
    output.add_argument('--outFileSortedRegions',
                        help='File name in which the regions are saved '
                        'after skiping zeros or min/max threshold values. The '
                        'order of the regions in the file follows the sorting '
                        'order selected. This is useful, for example, to '
                        'generate other heatmaps keeping the sorting of the '
                        'first heatmap. Example: Heatmap1sortedRegions.bed',
                        metavar='BED file',
                        type=argparse.FileType('w'))
    return parser


def computeMatrixOptArgs(case=['scale-regions', 'reference-point'][0]):

    parser = argparse.ArgumentParser(add_help=False)
    optional = parser.add_argument_group('Optional arguments')
    optional.add_argument('--version', action='version',
                          version='%(prog)s {}'.format(__version__))

    if case == 'scale-regions':
        optional.add_argument('--regionBodyLength', '-m',
                              default=1000,
                              type=int,
                              help='Distance in bp to which all regions are '
                              'going to be fitted.')
        optional.add_argument('--startLabel',
                              default='TSS',
                              help='Label shown in the plot for the start of '
                              'the region. Default is TSS (transcription '
                              'start site), but could be changed to anything, '
                              'e.g. "peak start". Note that this is only '
                              'useful if you plan to plot the results yourself '
                              'and not, for example, with heatmapper, which '
                              'will override this.')
        optional.add_argument('--endLabel',
                              default='TES',
                              help='Label shown in the plot for the region '
                              'end. Default is TES (transcription end site).'
                              'See the --startLabel option for more '
                              'information. ')
        optional.add_argument('--beforeRegionStartLength', '-b', '--upstream',
                              default=0,
                              type=int,
                              help='Distance upstream of the start site of '
                              'the regions defined in the region file. If the '
                              'regions are genes, this would be the distance '
                              'upstream of the transcription start site.')
        optional.add_argument('--afterRegionStartLength', '-a', '--downstream',
                              default=0,
                              type=int,
                              help='Distance downstream of the end site '
                              'of the given regions. If the '
                              'regions are genes, this would be the distance '
                              'downstream of the transcription end site.')

    elif case == 'reference-point':
        optional.add_argument('--referencePoint',
                              default='TSS',
                              choices=['TSS', 'TES', 'center'],
                              help='The reference point for the plotting '
                              'could be either the region start (TSS), the '
                              'region end (TES) or the center of the region. '
                              'Note that regardless of what you specify, '
                              'heatmapper will default to using "TSS" as the '
                              'label.')

        # set region body length to zero for reference point mode
        optional.add_argument('--regionBodyLength', help=argparse.SUPPRESS,
                              default=0, type=int)
        optional.add_argument('--beforeRegionStartLength', '-b', '--upstream',
                              default=500,
                              type=int,
                              metavar='INT bp',
                              help='Distance upstream of the reference-point '
                              'selected.')
        optional.add_argument('--afterRegionStartLength', '-a', '--downstream',
                              default=1500,
                              metavar='INT bp',
                              type=int,
                              help='Distance downstream of the '
                              'reference-point selected.')
        optional.add_argument('--nanAfterEnd',
                              action='store_true',
                              help='If set, any values after the region end '
                              'are discarded. This is useful to visualize '
                              'the region end when not using the '
                              'scale-regions mode and when the reference-'
                              'point is set to the TSS.')

    optional.add_argument('--binSize', '-bs',
                          help='Length, in base pairs, of the non-overlapping '
                          'bin for averaging the score over the '
                          'regions length.',
                          type=int,
                          default=10)

    optional.add_argument('--sortRegions',
                          help='Whether the output file should present the '
                          'regions sorted. The default is to not sort the regions.'
                          ' Note that this is only useful if you plan to plot '
                          'the results yourself and not, for example, with '
                          'heatmapper, which will override this.',
                          choices=["descend", "ascend", "no"],
                          default='no')

    optional.add_argument('--sortUsing',
                          help='Indicate which method should be used for '
                          'sorting. The value is computed for each row.',
                          choices=["mean", "median", "max", "min", "sum",
                                   "region_length"],
                          default='mean')

    optional.add_argument('--averageTypeBins',
                          default='mean',
                          choices=["mean", "median", "min",
                                   "max", "std", "sum"],
                          help='Define the type of statistic that should be '
                          'used over the bin size range. The '
                          'options are: "mean", "median", "min", "max", "sum" '
                          'and "std". The default is "mean".')

    optional.add_argument('--missingDataAsZero',
                          help='Set to "yes", if missing data should be '
                          'indicated as zeros. The default is to ignore such '
                          'cases, which will be depicted as black areas in '
                          'the heatmap. (see the --missingDataColor argument '
                          'of the heatmapper command for additional options).',
                          action='store_true')

    optional.add_argument('--skipZeros',
                          help='Whether regions with only scores of zero '
                          'should be included or not. Default is to include '
                          'them.',
                          action='store_true')

    optional.add_argument('--minThreshold',
                          default=None,
                          type=float,
                          help='Numeric value. Any region containing a '
                          'value that is equal or less than this numeric '
                          'value will be skipped. This is useful to skip, '
                          'for example, genes where the read count is zero '
                          'for any of the bins. This could be the result of '
                          'unmappable areas and can bias the overall results.')

    optional.add_argument('--maxThreshold',
                          default=None,
                          type=float,
                          help='Numeric value. Any region containing a value '
                          'that is equal or higher that this numeric value '
                          'will be skipped. The maxThreshold is useful to '
                          'skip those few regions with very high read counts '
                          '(e.g. major satellites) that may bias the average '
                          'values.')

    # in contrast to other tools,
    # computeMatrix by default outputs
    # messages and the --quiet flag supresses them
    optional.add_argument('--quiet', '-q',
                          help='Set to remove any warning or processing '
                          'messages.',
                          action='store_true')

    optional.add_argument('--scale',
                          help='If set, all values are multiplied by '
                          'this number.',
                          type=float,
                          default=1)
    optional.add_argument('--numberOfProcessors', '-p',
                          help='Number of processors to use. Type "max/2" to '
                          'use half the maximum number of processors or "max" '
                          'to use all available processors.',
                          metavar="INT",
                          type=numberOfProcessors,
                          default=cfg.config.get('general',
                                                 'default_proc_number'),
                          required=False)
    return parser


def process_args(args=None):
    args = parse_arguments().parse_args(args)

    if args.quiet is False:
        args.verbose = True
    else:
        args.verbose = False

    if args.command == 'scale-regions':
        args.nanAfterEnd = False
        args.referencePoint = None
    elif args.command == 'reference-point':
        if args.beforeRegionStartLength == 0 and \
                args.afterRegionStartLength == 0:
            sys.stderr.write("\nUpstrean and downstream regions are both "
                             "set to 0. Nothing to output. Maybe you want to "
                             "use the scale-regions mode?\n")
            exit()

    return(args)


def main(args=None):
    r"""
    >>> import filecmp
    >>> import os
    >>> args = parseArguments("reference-point \
    ... -R ../deeptools/test/test_heatmapper/test2.bed \
    ... -S ../deeptools/test/test_heatmapper/test.bw \
    ... -b 100 -a 100 --outFileName /tmp/_test.mat.gz \
    ... -bs 1 -p 1".split())
    >>> main(args)
    >>> os.system('gunzip -f /tmp/_test.mat.gz')
    0
    >>> filecmp.cmp('../deeptools/test/test_heatmapper/master.mat',
    ... '/tmp/_test.mat')
    True
    >>> os.remove('/tmp/_test.mat')
    >>> args = parseArguments("scale-regions \
    ... -R ../deeptools/test/test_heatmapper/test2.bed \
    ... -S ../deeptools/test/test_heatmapper/test.bw \
    ... -b 100 -a 100 -m 100 --outFileName /tmp/_test2.mat.gz \
    ... -bs 10 -p 1".split())
    >>> main(args)
    >>> os.system('gunzip -f /tmp/_test2.mat.gz')
    0
    >>> filecmp.cmp('../deeptools/test/test_heatmapper/master_scale_reg.mat',
    ... '/tmp/_test2.mat')
    True
    >>> os.remove('/tmp/_test2.mat')
    """

    args = process_args(args)

    # concatenate intermediary bedgraph files
    bed_file = open(deeptools.utilities.getTempFileName(suffix='.bed'), 'w+t')
    if args.verbose:
        print "temporary bed file {} created".format(bed_file.name)

    if len(args.regionsFileName) > 1:
        for bed in args.regionsFileName:
            bed.close()
            # concatenate all intermediate tempfiles into one
            print "appending {} file".format(bed.name)
            shutil.copyfileobj(open(bed.name, 'U'), bed_file)
            # append hash and label based on the file name
            label = os.path.basename(bed.name)
            if label.endswith(".bed"):
                label = label[:-4]
            bed_file.write("# {}\n".format(label))
        bed_file.seek(0)
    else:
        bed_file = args.regionsFileName[0]

    parameters = {'upstream': args.beforeRegionStartLength,
                  'downstream': args.afterRegionStartLength,
                  'body': args.regionBodyLength,
                  'bin size': args.binSize,
                  'ref point': args.referencePoint,
                  'verbose': args.verbose,
                  'bin avg type': args.averageTypeBins,
                  'missing data as zero': args.missingDataAsZero,
                  'min threshold': args.minThreshold,
                  'max threshold': args.maxThreshold,
                  'scale': args.scale,
                  'skip zeros': args.skipZeros,
                  'nan after end': args.nanAfterEnd,
                  'proc number': args.numberOfProcessors,
                  'sort regions': args.sortRegions,
                  'sort using': args.sortUsing
                  }

    hm = heatmapper.heatmapper()

    scores_file_list = [x.name for x in args.scoreFileName]
    hm.computeMatrix(scores_file_list, bed_file, parameters, verbose=args.verbose)
    if args.sortRegions != 'no':
        hm.matrix.sort_groups(sort_using=args.sortUsing, sort_method=args.sortRegions)

    hm.saveMatrix(args.outFileName)
    bed_file.close()
    #os.remove(bed_file.name)

    if args.outFileNameMatrix:
        hm.saveMatrixValues(args.outFileNameMatrix)

    #TODO This isn't implemented
    #if args.outFileNameData:
    #    hm.saveTabulatedValues(args.outFileNameData)

    if args.outFileSortedRegions:
        hm.saveBED(args.outFileSortedRegions)