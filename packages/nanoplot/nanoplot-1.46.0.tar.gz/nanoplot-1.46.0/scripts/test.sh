#!/bin/bash
set -ev

if [ -d "nanotest" ]; then
    echo "nanotest already cloned"
else
    git clone https://github.com/wdecoster/nanotest.git
fi

NanoPlot -h
NanoPlot --listcolors
NanoPlot --listcolormaps
NanoPlot --version

echo "testing figformat pdf with:"
NanoPlot --bam nanotest/alignment.bam --verbose -o tests -o tests --format pdf --drop_outliers
echo "testing fasta with --tsv_stats:"
NanoPlot --fasta nanotest/reads.fa.gz --verbose --maxlength 35000 -o tests --tsv_stats
echo "testing bam:"
NanoPlot --bam nanotest/alignment.bam --verbose -o tests --title testing
echo "testing bam without supplementary alignments:"
NanoPlot --bam nanotest/alignment.bam --verbose --no_supplementary -o tests
echo "testing summary:"
NanoPlot --summary nanotest/sequencing_summary.txt --loglength --verbose -o tests
echo "testing fastq rich:"
NanoPlot --fastq_rich nanotest/reads.fastq.gz --verbose --downsample 800 -o tests
echo "testing fastq minimal:"
NanoPlot --fastq_minimal nanotest/reads.fastq.gz --store --verbose --plots dot -o tests
echo "testing fastq plain:"
NanoPlot --fastq nanotest/reads.fastq.gz --verbose --minqual 4 --color red -o tests
echo "testing fasta:"
NanoPlot --fasta nanotest/reads.fa.gz --verbose --maxlength 35000 -o tests
echo "testing --no_static:"
NanoPlot --summary nanotest/sequencing_summary.txt  --verbose --maxlength 35000 -o tests --no_static

# echo "testing legacy with summary:"
# echo "installing seaborn and an appropriate version of numpy" # fuck this
# pip install seaborn==0.10.1 "numpy<1.24"
# NanoPlot --summary nanotest/sequencing_summary.txt --loglength --verbose -o tests --legacy hex --raw -p prefix --plots dot
# echo "testing legacy with multiple output formats:"
# NanoPlot --summary nanotest/sequencing_summary.txt --loglength --verbose -o tests --legacy hex --raw -p prefix --plots dot --format pdf png jpeg

# Add these 8 lines to the existing test.sh:

echo "testing cram with multiple formats and filtering:"
NanoPlot --cram nanotest/alignment.cram --verbose -o tests --format png jpeg --minlength 1000 --maxlength 40000

echo "testing multiple plot types with N50:"
NanoPlot --summary nanotest/sequencing_summary.txt --plots kde dot --N50 --verbose -o tests

echo "testing colormap and title with quality filtering:"
NanoPlot --bam nanotest/alignment.bam --colormap Viridis --title "Test Run" --minqual 8 --verbose -o tests

echo "testing info_in_report with downsample:"
NanoPlot --summary nanotest/sequencing_summary.txt --info_in_report --downsample 500 --verbose -o tests

echo "testing barcoded and threads (will show warning):"
NanoPlot --summary nanotest/sequencing_summary.txt --barcoded --threads 2 --verbose -o tests

echo "testing huge mode with custom prefix:"
NanoPlot --fastq nanotest/reads.fastq.gz --huge --prefix test_ --verbose -o tests

echo "testing only_report mode:"
NanoPlot --summary nanotest/sequencing_summary.txt --only_report --verbose -o tests

echo "testing version and listcolormaps:"
NanoPlot --version
NanoPlot --listcolormaps