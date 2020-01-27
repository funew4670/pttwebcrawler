
from bs4 import BeautifulSoup
import re

output = []


with open('coolpc.txt','r',encoding="utf-8") as f:
    content = f.read()    
    
    soup = BeautifulSoup(content, 'html.parser')
    list_tr =  soup.tbody.find_all('tr')
    #print (len(list_tr))    
    #print(a)
    i = 0
    for tr in list_tr:
        print("")
        print(i)        
        content_td = ""
        content_td = tr.contents[2]
        list_optgroup = content_td.find_all('optgroup')        
        if (len(list_optgroup)!=0):
            i += 1
            #print(len(list_optgroup))
        for gpname in list_optgroup:
            print("")
            print(gpname.attrs['label'])
            #output.append(gpname.attrs['label'])
            gp = gpname.find_all('option')            
            for value in gp :
                sSplit = value.string.split(",")
                if (len(sSplit)<2):
                    continue
                iPrice = re.findall(r"\$\d+",sSplit[1])
                if not iPrice:
                    continue
                sItem = sSplit[0] + " " + iPrice[0]
                print(sItem)                
                output.append(sItem)
    
        print("")
    
text_file = open("output.txt","w",encoding="utf-8")
for strs in output:
    text_file.write(strs+ "\n")
text_file.close

