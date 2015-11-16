# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 14:11:54 2015

@author: Alex
"""

from lxml import html
import os
import requests

SCRIPT_DIRECTORY = os.getcwd()

"""Takes tree and returns a list mapping the available plays in the form of their url extensions,
e.g. "errors" for "The Comedy of Errors" meaning http://nfs.sparknotes.com/errors is the root page
for that play"""
def getPlayExtensions(tree):
    playExtensions = []   
    
    oddPlayEntries = tree.xpath('//div[@class="entry odd"]')
    evenPlayEntries = tree.xpath('//div[@class="entry even"]')
    oddPlayEntries.extend(evenPlayEntries)
    
    for entry in oddPlayEntries:
        links = [link for link in entry.iterlinks()]
        playName = links[0][2]
        playName = playName[:-1] #remove trailing slash
        playExtensions.append(playName)
    playExtensions = playExtensions[:-1] #last entry is a list of available titles
    playExtensions.remove("sonnets") #only do plays for now
    return playExtensions

"""Takes in the root url for a NFS play page (assumes not a sonnet)
Returns [allOriginalText, allModernText] corresponding to the original and modern Shakespeare play text.
Each is a list of lists, the outer list corresponds to table entires
The inner list corresponds to the lines in that table entry
The outer list should be of the same size for modern and original text
The inner lists are not guaranteed to be of the same size based on how NFS is structured"""    
def readPlay(playUrl):
    playPage = requests.get(playUrl)
    playTree = html.fromstring(playPage.content)
    
    actHeading = playTree.xpath('//p[@class="heading"]')
    firstSectionOfAct = actHeading[0].getnext()
    firstLink = [link for link in firstSectionOfAct.iterlinks()][0][2] #link to the first page of the play
    
    def getAllPageLinks():
        firstPage = requests.get(firstLink)
        firstTree = html.fromstring(firstPage.content)
        
        dropdownDiv = firstTree.xpath('//div[@class="dropdownMenu is-centered"]')[0]
        optionList = dropdownDiv.getchildren()[0].getchildren()[0].getchildren()
        allPageLinks = [option.values()[0] for option in optionList]
        return allPageLinks[2:-1] #remove the root, citing and the characters page links
    
    """Takes in the string url to a specific page of the play. Returns two lists, first for the original text
    second for the modern text version. Each list is a list of lists. The outer list denotes table entries as used
    by NFS. The modern table entries should have a one to one correspondence with the original table entries (i.e.
    originalText[i] should be the original version of modernText[i]. The inner list is the individual lines within that table
    entry. Note that the modern text is not necessarily broken up into lines, so there is no implied relationship between line numbers
    for original and modern."""
    def readPageLink(pageLink):
        singlePage = requests.get(pageLink)
        singleTree = html.fromstring(singlePage.content)
        
        #each of these is a list of the table entries. this assumes the order of original td's and modern td's
        #correspond 1 to 1 and are in order
        originalTds = singleTree.xpath('//td[@class="noFear-left"]')[1:] #don't include heading
        modernTds = singleTree.xpath('//td[@class="noFear-right"]')[1:] #don't include heading
        
        
        
        def sanitizeText(t):
            t = str(t.encode('utf-8').decode('ascii', 'ignore'))
            t = t.replace("\n","")
            t = t.replace("\t", "")
            
            tList = t.split(" ")
            
            outputString = ""
            for word in tList:
                if len(word) > 0:
                    outputString += word
                    outputString += " "       
            return outputString[:-1] #removes trailingSpace
        
        #Takes in a list of the td's. Returns a list of lists, the outer list corresponds to table entires
        #The inner list corresponds to the lines in that table entry
        #The outer list should be of the same size for modern and original text
        #The inner lists are not guaranteed to be of the same size based on how NFS is structured
        def readLines(tdList):
            text = []
            for td in tdList:
                newEntry = []
                children = td.getchildren()
                for lineDiv in children:
                    lineDivValues = lineDiv.values()
                    if len(lineDivValues) > 0:   
                        divClass = lineDivValues[0]
                        #don't include stage directions
                        if divClass == "original-stage" or divClass == "modern-stage":
                            continue
                    unsanitized = lineDiv.text_content()
                    sanitized = sanitizeText(unsanitized)
                    newEntry.append(sanitized)
                if len(newEntry) > 0:
                    text.append(newEntry)
            return text
            
        originalText = readLines(originalTds)
        modernText = readLines(modernTds)
            
        return [originalText, modernText]
        
    allPageLinks = getAllPageLinks()
    
    allOriginalText, allModernText = [],[]
    for pageLink in allPageLinks:
        [pageOriginalText, pageModernText] = readPageLink(pageLink)
        allOriginalText.extend(pageOriginalText)
        allModernText.extend(pageModernText)
    return [allOriginalText, allModernText]
    
"""Takes the lists allOriginalText and allModernText for a single play
as output by readPlay. Also takes the outputFilePathPrefix, the name of the
output file for that play without the file extension, .txt

Writes the input lists (original to prefix_original.txt; modern to prefix_moder.txt)
as follows:
<T>: a line to distinguish start of a table entry on the NFS website
Line: each line from the NFS website on a separate line of the text file
</T>: a line to distinguish the end of a table entry on the NFS website"""    
def writePlay(allOriginalText, allModernText, outputFilePathPrefix):
    originalFilePath = outputFilePathPrefix + "_original.txt"
    modernFilePath = outputFilePathPrefix + "_modern.txt"
    
    def writePlayVersion(versionText, versionFilePath):
        f = open(versionFilePath, "wb")
        for tableEntry in versionText:
            f.write("<T>\n")
            for line in tableEntry:
                f.write(line + "\n")
            f.write("</T>\n")
        f.close()
    
    writePlayVersion(allOriginalText, originalFilePath)
    writePlayVersion(allModernText, modernFilePath)
                
        
        

def main():
    print "Starting..."
    rootAddress = 'http://nfs.sparknotes.com/'
    rootPage = requests.get(rootAddress)
    rootTree = html.fromstring(rootPage.content)
    
    playExtensions = getPlayExtensions(rootTree)
    
    for (index, extension) in enumerate(playExtensions):
        print "Processing number:", index+1, "of", len(playExtensions), ": ", extension
        playUrl = rootAddress + extension + "/"
        outputFilePathPrefix = SCRIPT_DIRECTORY+ "/output/" + extension
        [allOriginalText, allModernText] = readPlay(playUrl)
        writePlay(allOriginalText, allModernText, outputFilePathPrefix)
    print "Finishing..."
main()