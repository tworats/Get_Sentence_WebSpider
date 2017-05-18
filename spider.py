from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
from pathlib import Path
import re
import os


def main():
    _url = input("Enter website: ")
    word = input("Enter keyword: ")
    maxPages = int(input("Enter the maximum number of pages to search: "))
    flname = input("Output file name (default is 'output'): ")
    frmat = input("Enter specified format (default is .csv): ")

    ow = "n"

    locdir = os.path.dirname(__file__)
    fdir = os.path.join(locdir, 'output_files')

    fname = "output"

    if flname != "":
        fname = flname
    else:
        fname = "output"

    if frmat == "":
        frmat = '.csv'
    elif frmat[0:1] != '.':
        frmat = '.' + frmat

    fllname = fname + frmat

    fldir = os.path.join(fdir, fllname)

    my_file = Path(fldir)

    if my_file.is_file():
        ow = input("Overwrite existing data? [Y/N]: ")

    if ow == 'Y' or ow == 'y':
        owv = "w"
    else:
        owv = "a+"

    if _url[0:4] != "http":
        url = "http://" + _url + "/"
    else:
        url = _url

    spider(url, word, maxPages, owv, fname, fdir, frmat)

class LinkParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        # We are looking for the begining of a link. Links normally look
        # like <a href="www.someurl.com"></a>
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    newUrl = parse.urljoin(self.baseUrl, value)
                    # And add it to our colection of links:
                    self.links = self.links + [newUrl]

    # This is a new function that we are creating to get links
    # that our spider() function will call
    def getLinks(self, url):
        self.links = []
        self.baseUrl = url
        response = urlopen(url)

        if response.getheader('Content-Type')=='text/html':
            htmlBytes = response.read()

            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            return htmlString, self.links
        else:
            return "",[]


# The spider. It takes in an URL, a word to find,
# and the number of pages to search through before giving up
def spider(url, word, maxPages, owv, fname, fdir, frmat):  
    pagesToVisit = [url]
    numberVisited = 0
    foundWord = False

    Sentences = []

    while numberVisited < maxPages and pagesToVisit != []:
        numberVisited = numberVisited +1
        # Start from the beginning of our collection of pages to visit:
        url = pagesToVisit[0]
        pagesToVisit = pagesToVisit[1:]
        try:
            print(numberVisited, "Visiting:", url)
            parser = LinkParser()
            data, links = parser.getLinks(url)
            if data.find(word)>-1:
                foundWord = True
                newdata = re.sub('<[^<]+?>', '', data)
                newdata = newdata.replace('"', '')
                newdata = newdata.replace('\t', '.')
                newdata = newdata.replace('\n', '.')
                newdata = newdata.replace('&amp;', '&')
                newdata = newdata.replace('&nbsp;', ' ')
                newdata = newdata.replace('&mdash;', ' — ')    
                newdata = newdata.replace('&ldquo;', '')
                newdata = newdata.replace('&rdquo;', '')
                fword = word
                retrieved = [sentence + '.' for sentence in newdata.split('.') if fword in sentence and '!' not in sentence and '?' not in sentence]
                retrieved.extend([sentence + '!' for sentence in newdata.split('!') if fword in sentence and '?' not in sentence and '.' not in sentence])
                retrieved.extend([sentence + '?' for sentence in newdata.split('?') if fword in sentence and '!' not in sentence and '.' not in sentence])

                print(retrieved)
                Sentences.extend(retrieved)
                # Add the pages that we visited to the end of our collection
                # of pages to visit:
                pagesToVisit = pagesToVisit + links
                print(" **Success!**")
        except:
            print(" **Failed!**")

    if foundWord:
        print("The word", "'"+word+"'", "was found at", url)
        print("Sentences retrieved:", Sentences)
        
        filewrite(Sentences, owv, fname, fdir, frmat)

    else:
        print("Word", "'"+word+"'", "not found!")

def filewrite(Sentences, owv, fname, fdir, frmat):
    if not os.path.exists(fdir):
        os.makedirs(fdir)

    newdir = os.path.join(fdir, fname)

    output_file = open(newdir + frmat, owv)
    ct = 0

    if owv == 'a+':
        flines = output_file.readlines()

        ct = len(flines) - 1

    for each_sentence in Sentences:
        ct = ct + 1 
        stc = str(ct) + "," + '"' + each_sentence + '"' + "\n"
        output_file.write(stc)

    output_file.close()


if __name__ == '__main__':
    main()
