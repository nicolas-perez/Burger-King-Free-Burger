import datetime
import random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

"""
Script qui répond automatiquement au questionnaire de satisfaction de Burger King (25 pages). A la fin du questionnaire, on obtient un code permettant d'avoir un burger gratuit pour un menu acheté lors de la prochaine commande. Il suffit d'écrire ce code au dos d'un ticket de caisse datant de moins de 30 jours et se présenter en caisse.

Puisque certaines réponses sont susceptibles de déclencher des enquêtes internes si l'on remplit n'importe quoi (exemples: Répondre "oui" à la question "Avez-vous eu des problèmes lors de votre expérience chez BURGER KING® ?", répondre "très insatisfait" pour la propreté, etc), on veille à ce que les réponses reflètent toujours celles d'un client satisfait. 

Fonctionne à 100% à la date du dernier commit. 
"""

chromedriver = 'chromedriver.exe'

if __name__ == "__main__":

    driver = webdriver.Chrome(chromedriver)
    driver.implicitly_wait(5)
    driver.get("https://www.bkvousecoute.fr/")
    driver.find_element_by_id("NextButton").click()

    ref_restaurant = '22924' #BK Toulouse Labège
    driver.find_element_by_name("SurveyCode").send_keys(str(ref_restaurant))
    
    #Génération d'une date et heure de commande aléatoire comprise dans les 3 à 14 jours précédents
    now = datetime.datetime.now()
    three_to_fourteen_days = datetime.timedelta(seconds=random.randint(3*24*60*60, 14*24*60*60))
    random_order_datetime = now - three_to_fourteen_days
    day, month, year, hour, minutes = random_order_datetime.strftime("%d %m %y %H %M").split()

    #Input date et heure
    Select(driver.find_element_by_id('InputDay')).select_by_visible_text(day)
    Select(driver.find_element_by_id('InputMonth')).select_by_visible_text(month)
    Select(driver.find_element_by_id('InputYear')).select_by_visible_text(year)
    Select(driver.find_element_by_id('InputHour')).select_by_visible_text(hour)
    Select(driver.find_element_by_id('InputMinute')).select_by_visible_text(minutes)
    driver.find_element_by_id("NextButton").click()

    while 'Merci de votre participation' not in driver.page_source:

        #Cas particuliers des pages où il ne faut pas répondre au hasard
        if 'Avez-vous eu des problèmes lors de votre expérience chez BURGER KING® ?' in driver.page_source:
            index_non = [e.text for e in driver.find_element_by_xpath('//*[@id="surveyQuestions"]/table/tbody/tr[1]').find_elements_by_tag_name('td')[1:]].index('Non')
            driver.find_element_by_xpath('//*[@id="FNSR041000"]/td[{non}]/span'.format(non=index_non+2)).click()
        
        elif "Merci d'évaluer votre satisfaction générale en ce qui concerne la résolution de votre problème." in driver.page_source:
            driver.find_element_by_xpath('//*[@id="FNSR042000"]/td[7]/span').click() #N/A
        
        elif 'Est-ce que la commande reçue était complète et conforme à ce que vous aviez demandé ?' in driver.page_source:
            index_oui = [e.text for e in driver.find_element_by_xpath('//*[@id="surveyQuestions"]/table/tbody/tr[1]').find_elements_by_tag_name('td')[1:]].index('Oui')
            driver.find_element_by_xpath('//*[@id="FNSR049000"]/td[{oui}]/span'.format(oui=index_oui+2)).click()
        
        elif 'Parmi les propositions suivantes, laquelle décrit le mieux la raison de votre visite chez BURGER KING® ?' in driver.page_source:
            for option in driver.find_element_by_xpath('//*[@id="FNSR060000"]/div[2]').find_elements_by_class_name('rbloption'):
                if 'Le type de nourriture proposé' in option.text:
                    option.find_element_by_class_name('radioBranded').click()

        #Cas de toutes les autres pages, où l'on donne des réponses aléatoirement comme un client satisfait
        else:
            survey_elements = driver.find_elements_by_css_selector('div#surveyQuestions>*')[:-4]
            for survey_element in survey_elements:
                if survey_element.tag_name == 'table':
                    for ligne in survey_element.find_elements_by_tag_name('tr')[1:]:
                        colonne_aleatoire = random.choice(ligne.find_elements_by_tag_name('td')[1:3])
                        colonne_aleatoire.find_element_by_tag_name('span').click()
            
                elif survey_element.tag_name == 'div' and survey_element.get_attribute('class') == 'FNSITEM inputtyperblv':
                    random.choice(survey_element.find_elements_by_class_name('rbloption')).find_element_by_tag_name('span').click()
                
                elif survey_element.tag_name == 'div' and survey_element.get_attribute('class') == 'FNSITEM inputtypetxt':
                    pass #On n'a pas besoin de remplir les champs de texte
                
                elif survey_element.tag_name == 'div' and survey_element.get_attribute('class') == 'FNSITEM inputtypeddl':
                    random.choice(survey_element.find_elements_by_tag_name('option')[1:]).click()
                
                elif survey_element.tag_name == 'div' and survey_element.get_attribute('class') == 'inputtypeopt':
                    random_element = random.choice(survey_element.find_elements_by_class_name('cataOption')[:-2])
                    random_element.find_element_by_class_name('checkboxBranded').click()

        driver.find_element_by_id("NextButton").click()

    print(driver.find_element_by_xpath('//*[@id="FNSfinishText"]/div/p[2]').text)