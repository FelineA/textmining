import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup, Tag, NavigableString
import pickle
from multiprocessing import Pool, cpu_count
import pandas as pd

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/35.0.1916.47 Safari/537.36'
url_avatar_spec = "https://www.allocine.fr/film/fichefilm-61282/critiques/spectateurs/"



#***********************************************************************************************************************
# function : n_stop
# param : bsObj a beautifulSoup object
# do : check if we are at the last page 
# return : 1 if we are at the last page of the categorie esle 0
#***********************************************************************************************************************


def n_stop(bsObj):
    pagination = bsObj.find("nav",{"class": "pagination"}).find_all("span")
    
    for span in pagination :
        if span.find("span")!= None:  
            if ( span.find("span").text == 'Suivante') & ("button-disabled" in span['class'] ):
              return(0)        
    return(1)
                
    
    
#***********************************************************************************************************************
# function : collecte_articles
# param : url a string with url from a category of the canadian encyclopedia
# do : create a liste of url of the categorie page 
# return : liste of strings 
#***********************************************************************************************************************
                
def collecte_avis(url):
    page = 1
    req = Request(url,headers={'User-Agent':user_agent})
    try: # gestion des exceptions avec un bloc try/except
        html = urlopen(req)
    except (HTTPError, URLError) as e:
        sys.exit(e) # sortie du programme avec affichage de l’erreur
    liste_avis = []
    liste_personne = []
    liste_note = []
    liste_date = []
    
    bsObj = BeautifulSoup(html, "lxml") # en utilisant le parser de lxml
    while n_stop(bsObj): 
        if page != 1 :
            full_url  = url+ "?page=" + str(page)        
            req = Request(full_url,headers={'User-Agent':user_agent})
            try: # gestion des exceptions avec un bloc try/except
                html = urlopen(req)
            except (HTTPError, URLError) as e:
                sys.exit(e) # sortie du programme avec affichage de l’erreur
            
            bsObj = BeautifulSoup(html, "lxml") # en utilisant le parser de lxml
            

        l_avis = bsObj.find_all("div",{"class": "review-card"})
        #avis = l_avis[1]
        for avis in l_avis :
            liste_note.append(avis.find("div",{"class": "review-card-meta"}).find("div",{"class": "stareval"}).find("span",{"class": "stareval-note"}).text)
            date = avis.find("div",{"class": "review-card-meta"}).find("span",{"class": "review-card-meta-date"}).text            
            liste_date.append(date.replace("\n", "", 2))           
            avis_text = avis.find("div",{"class": "review-card-content"}).text        
            liste_avis.append( avis_text.replace("\n", "", 2))                               
            liste_personne.append(avis.find("div",{"class": "review-card-aside"}).find("div",{"class": "review-card-user-infos"}).find("div",{"class": "meta"}).find("div",{"class": "meta-title"}).find("span").text)
    #
        page += 1
    
    df = pd.DataFrame(list(zip(liste_personne,liste_note, liste_date,liste_avis)),
               columns =['Nom', 'Note','Date','Avis'])

    return(df)
    
    
avis = collecte_avis(url_avatar_spec)

avis.to_csv(r'C:\Users\remye\Desktop\M2\Text mining\avis.csv', index = False, header=True)