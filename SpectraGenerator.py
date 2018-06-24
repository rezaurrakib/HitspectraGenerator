import csv
import tkinter
import codecs
from html.parser import HTMLParser
from tkinter.filedialog import askopenfilename

__author__ = "Reza, Technical University of Munich"
__email__ = "reza.rahman@tum.de"

class HitspectraGenrator():
    def __init__(self):
        self.function_names = []
        self.filepaths = []
        self.htmlfiles = []
        self.temp_dict = {}
        self.isfirst = False

    def get_html_files(self):        
        root = tkinter.Tk()
        root.withdraw()
        self.filepaths = tkinter.filedialog.askopenfilenames(parent=root,title='Choose Multiple HTML files')
        print(list(self.filepaths))
    
    def get_html_astring(self):
        for path in self.filepaths:
            fdata = codecs.open(path, 'r')
            str = fdata.read()
            self.htmlfiles.append(str)
            
    def write_function_names(self, funclist):
        # Save the func_name list in the first row of the csv file for future use
        self.function_names = funclist
        funclist.insert(0,"Index")
        funclist.insert(len(funclist), "Result")
        file = open("functions_call_hit_spectra.csv", "w")
        out = csv.writer(file, delimiter=';', lineterminator='\n', quoting=csv.QUOTE_ALL)
        out.writerow(funclist)
       
    def write_function_hitcount(self, func_names, funs_hitcnt_dict):
        # Creating dummy list for wirting the hitcount list in the csv file
        
        ## TODO : Fix what should be the name of the test cases in the first column and how ##
        ## we should put the value in the last Result column, need to discuss. Temporarily, ##
        ## I put fixed value "TC" in the first column and "1" in the last "Result" column   ## 
        hit_list = []
        for name in func_names:
            if name == 'Index':
                hit_list.append('TC')
            elif name == 'Result':
                hit_list.append('1') # Dummy value 1 in column "Result"
            else:
                hit_list.append(funs_hitcnt_dict.get(name))
        
        # Writing the list in the csv file
        file = open("functions_call_hit_spectra.csv", "a")
        out = csv.writer(file, delimiter=';', lineterminator='\n', quoting=csv.QUOTE_ALL)
        out.writerow(hit_list)
        
    # Create key-value pair of (func, hitcount) tuple for each Test case
    def create_dictionary(self, funclist, hitcountlist):
        for i in range(len(funclist)):
            self.temp_dict[funclist[i]] = hitcountlist[i] 
        #print(self.temp_dict.items())
        

## Class for parsing HTML and retreiving function names and hitcount

class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.funcounter = 0
        self.hitcounter = 0
        self.func_data = []
        self.hitcount_data = []
        
    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            for name, value in attrs:
                #print("Encountered the beginning of a %s tag" % tag)
                if name == 'class' and value == 'coverFn':
                    self.funcounter = 1
                if name == 'class' and value == 'coverFnHi':
                    self.hitcounter = 1
        
    def handle_endtag(self, tag):
        if tag == 'td':
            if(self.funcounter): 
                self.funcounter -=1 
            if(self.hitcounter):
                self.hitcounter -=1                      
        
    def handle_data(self, data):
        if self.funcounter:
            self.func_data.append(data)
            #print('Function Name : ', data)
        elif self.hitcounter:
            self.hitcount_data.append(data)
            #print('Function Hitcount: ', data)
   
if __name__ == '__main__':
    obj = HitspectraGenrator()
    obj.get_html_files()
    obj.get_html_astring()
    
    # Read all html files and Extract hitcount and func names
    for html in obj.htmlfiles:
        parserobj = Parser()
        str = html
        #print(str)
        parserobj.feed(str)
        #print(parserobj.func_data)
        #print(parserobj.hitcount_data)
        obj.temp_dict = {} # Reset dictionary for each hitcount row
        obj.create_dictionary(parserobj.func_data, parserobj.hitcount_data)

        # Writing data in csv file
        if obj.isfirst == False: # For the Ist time, write both func name and hitcount
            obj.isfirst = True 
            obj.write_function_names(parserobj.func_data)
            obj.write_function_hitcount(obj.function_names, obj.temp_dict)
        else:
            obj.write_function_hitcount(obj.function_names, obj.temp_dict)
        
    
