No Fear Shakespeare Web Scraper
==============================
#Function:

Scrapes the original and "modern" No Fear Shakespeare play text from http://nfs.sparknotes.com/

Writes the output files for the original and modern play versions to an output folder that is assumed to be in the same directory that the script is run in. Writes the input lists (original to prefix_original.txt; modern to prefix_moder.txt) as follows: 

\<T\>: a line to distinguish start of a table entry on the NFS website 

Line: each line from the NFS website on a separate line of the text file 

\</T\>: a line to distinguish the end of a table entry on the NFS website.

#Intended Use:

This text will be used as training data for a machine translation model. The goal is to translate original Shakespeare into modern English and in iambic pentameter following some of the idea from this paper http://www.aclweb.org/anthology/D10-1051

