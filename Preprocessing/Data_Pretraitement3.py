import json
import spacy
import Parameters as parameters
import Preprocessing.Data_Pretraitement as dp1
from langdetect import detect
from sentence_splitter import SentenceSplitter, split_text_into_sentences
from SPARQLWrapper import SPARQLWrapper, JSON

def lematize_text(texte):
    nlp = spacy.load('fr_core_news_md')
    doc = nlp(texte)
    lst_lema = [token.lemma_ for token in doc]
    lst_pos = [token.pos_ for token in doc]
    lst_tokens = [token for token in doc]
    return lst_tokens, lst_lema, lst_pos

file_folder = parameters.file_folder()

'''Crée le Train data de format texte et liste des entite aux positions corespondantes 
Arguments: None
Returns:   Train Data'''
def process_styles_artistiques_data():
    with open(file_folder + "Process_data/Dictionary_approach/" + "styles_artistiques.json") as json_file:
        styles_artistiques_data = json.load(json_file)

    lst_entities_types = ["ADJ", "ADV", "NOUN", "NUM", "VERB", "PROPN"]
    dict_styles_artistiques_data = {}
    for p in styles_artistiques_data:
        # print(p) #p = DOMAINE, EPOQUE, LOCALISATION, PERIODE, TECHNIQUE
        # print(data[p]) # data[p] = list des p
        dict_p = {}
        lst_terms_p = styles_artistiques_data[p]
        #lst_terms_p_lem = []
        for terms_p in lst_terms_p:
            if terms_p:
                token_terms_p, lem_terms_p, pos_terms_p = lematize_text(terms_p)
                #print(lem_terms_p)
                lst_terms_p_lem = []
                for index in range(len(lem_terms_p)):
                    if pos_terms_p[index] in lst_entities_types:
                        lst_terms_p_lem.append(lem_terms_p[index].lower())

                if len(lst_terms_p_lem) > 0:
                    # Le premier mot est la clé on verifie son existance
                    key = lst_terms_p_lem[0]
                    if key not in dict_p.keys():
                        min_terms_lengh = 100
                        max_terms_lengh = 0
                        dict_p[key] = {"min_terms_lengh": min_terms_lengh,
                                       "max_terms_lengh": max_terms_lengh,
                                       "terms": []
                                       }
                        print("New key add => " + key)

                    word_lst_terms_p_lem = " ".join(lst_terms_p_lem)
                    #verifier que le term n'existe pas deja dans la liste
                    if word_lst_terms_p_lem not in dict_p[key]["terms"]:
                        min_terms_lengh = min(dict_p[key]["min_terms_lengh"], len(lst_terms_p_lem))
                        max_terms_lengh = max(dict_p[key]["max_terms_lengh"], len(lst_terms_p_lem))
                        current_lst_terms = dict_p[key]["terms"]#.append(word_lst_terms_p_lem)
                        current_lst_terms.append(word_lst_terms_p_lem)
                        dict_p[key] = {"min_terms_lengh": min_terms_lengh,
                                       "max_terms_lengh": max_terms_lengh,
                                       "terms": current_lst_terms
                                       }
                        #dict_p[key]["terms"].append(word_lst_terms_p_lem)

                        print(key + " values => ")
                        print(dict_p[key])
                        print(lst_terms_p_lem)

        dict_styles_artistiques_data[p] = dict_p
        #dict_styles_artistiques_data[p].extend(lst_terms_p_lem)
    dp1.write_json(dict_styles_artistiques_data, file_folder + "Process_data/Dictionary_approach/" + "dict_styles_artistiques_tokenize_lem.json")


def write_dict(lst_tag_sentences, filname=file_folder + "expo_fr_annotated_bio.txt"):
    with open(filname, "a") as text_file:
        for tag in lst_tag_sentences:
            text_file.write(tag["tag"] + "\t" + tag["word"] + "\n")
        text_file.write("\n")

'''def code_to_sentence(dict_sentence, sentence_code):
    return  [dict_sentence[x] for x in sentence_code]
'''
'''Crée le Train data de format texte et liste des entite aux positions corespondantes 
Arguments: None
Returns:   Train Data'''
def process_train_data3():
    with open(file_folder + "Process_data/Dictionary_approach/" + "dict_styles_artistiques_tokenize_lem.json") as json_file:
      styles_artistiques_data = json.load(json_file)

    with open(file_folder + "Process_data/Dictionary_approach/" + "expo_fr.txt", 'r') as file:
      document = file.readlines()

    lst_entities_types = ["ADJ", "ADV", "NOUN", "NUM", "VERB", "PROPN"]
    lst_tag_sentences = []
    percent = 0
    for sentence in document:
        sentence = sentence.replace('\n', '')
        percent += 1
        #token_sentence, lem_sentence, pos_sentence = None, None, None
        token_sentence, lem_sentence, pos_sentence = lematize_text(sentence)
        #Construction du dictionaire de la phrase
        dict_token_sentence = {}
        dict_tags_sentence = {}
        dict_lem_sentence = {}
        sentence_lem_code = []
        lst_all_sentence_lem_code = []
        for index in range(len(token_sentence)):
            dict_token_sentence[index] = token_sentence[index].text
            dict_tags_sentence[index] = "O" #Initialisation de tous les mots a O
            if pos_sentence[index] in lst_entities_types:
              dict_lem_sentence[index] = lem_sentence[index].lower()
              sentence_lem_code.append(index)

        lst_all_sentence_lem_code.append(sentence_lem_code)
        number_of_while = 0
        while True:
            number_of_while += 1
            stop = True
            for p in styles_artistiques_data:
                # print(p) #p = DOMAINE, EPOQUE, LOCALISATION, PERIODE, TECHNIQUE
                # print(data[p]) # data[p] = list des dictionnaire de p
                lst_key_done = []
                lst_dict_p = styles_artistiques_data[p]
                for key in lst_dict_p.keys():
                    if key not in lst_key_done:
                        sentence_lem_code_in_key = []
                        #Prendre les sous phrases dans laquelle se trouve la key
                        for one_sentence_lem_code in lst_all_sentence_lem_code:
                            one_sentence_lem_normal = [dict_lem_sentence[x] for x in one_sentence_lem_code]
                            if key in one_sentence_lem_normal:
                                sentence_lem_code_in_key.append((one_sentence_lem_normal.index(key), one_sentence_lem_code))
                        #Chercher les termes de la cle dans les sous phrases trouvé
                        if len(sentence_lem_code_in_key) > 0:
                            #print(type(lst_dict_keys[key]))
                            terms_in_key = lst_dict_p[key]["terms"]
                            min_terms_lengh = lst_dict_p[key]["min_terms_lengh"]
                            max_terms_lengh = lst_dict_p[key]["max_terms_lengh"]
                            terms_in_key.sort(key=lambda x: len(x.split()), reverse=True)#Sort bye lenght of number of words
                            for key_index, one_sentence_lem_code_in_key in sentence_lem_code_in_key:
                                terms_substract_code = one_sentence_lem_code_in_key[key_index:key_index+max_terms_lengh+1]
                                while len(terms_substract_code) >= min_terms_lengh:
                                    #print("len(terms_substract_code) => "+str(len(terms_substract_code)))
                                    terms_substract_normal = [dict_lem_sentence[x] for x in terms_substract_code]
                                    if " ".join(terms_substract_normal) in terms_in_key:
                                        #Mettre les le tags correspondant aux mots
                                        print("Key => " + key + " expressions trouvées => " + " ".join(terms_substract_normal))
                                        min_terms_substract_code = min(terms_substract_code)
                                        max_terms_substract_code = max(terms_substract_code)
                                        if min_terms_substract_code == max_terms_substract_code:
                                            dict_tags_sentence[terms_substract_code[0]] = "B-"+p
                                            #for ind in terms_substract_code:
                                            #   dict_tags_sentence[ind] = p
                                        else:
                                            dict_tags_sentence[terms_substract_code[0]] = "B-"+p
                                            for ind in range(min_terms_substract_code+1, max_terms_substract_code + 1):
                                                dict_tags_sentence[ind] = "I-"+p #p == Tag  de l'entite
                                        #Mis a jour de la liste des phrases
                                        left_child_sentence = one_sentence_lem_code_in_key[:key_index]
                                        right_child_sentence = one_sentence_lem_code_in_key[key_index+len(terms_substract_code)+1:]
                                        lst_all_sentence_lem_code.remove(one_sentence_lem_code_in_key)
                                        if len(left_child_sentence) > 0:
                                            lst_all_sentence_lem_code.append(left_child_sentence)
                                        if len(right_child_sentence) > 0:
                                            lst_all_sentence_lem_code.append(right_child_sentence)
                                        terms_substract_code = []
                                        stop = False

                                    else:
                                        terms_substract_code = terms_substract_code[:len(terms_substract_code) - 1]

            print("number_of_while => "+str(number_of_while))
            #print(lst_all_sentence_lem_code)
            if stop:
                break
        #print(dict_tags_sentence)
        for index in range(len(token_sentence)):
            lst_tag_sentences.append({"word": dict_token_sentence[index], "tag": dict_tags_sentence[index]})

        lst_tag_sentences.append({"word": "", "tag": ""})

        if percent % 200 == 0:
          write_dict(lst_tag_sentences, file_folder + "Process_data/Dictionary_approach/" + "expo_fr_annotated_bio.txt")
          lst_tag_sentences = []
        print(str(percent) + " completed")

    if len(lst_tag_sentences) > 0:
        write_dict(lst_tag_sentences, file_folder + "Process_data/Dictionary_approach/" + "expo_fr_annotated_bio.txt")
        #lst_tag_sentences = []

    print("End function")


def clean_expo_data():
    with open(file_folder + "Process_data/Dictionary_approach/" + "expo.txt", 'r') as file:
      document = file.readlines()

    lst_all_sentence = []
    splitter = SentenceSplitter(language='fr')
    percent = 0
    french = 0
    for sentence in document:
        percent += 1
        print(str(percent) + " completed")
        sentence = sentence.replace('\n', '')
        lst_sentence = splitter.split(text=sentence)
        if len(lst_sentence) > 1:
            print(lst_sentence)
        for s in lst_sentence:
            if detect(s) == "fr":
                lst_all_sentence.append(s)
                french += 1

    with open(file_folder + "Process_data/Dictionary_approach/" + "expo_fr.txt", "a") as text_file:
        for s in lst_all_sentence:
            text_file.write(s + "\n")

    print(str(french) + " french sentences")
    print("End function")

import requests

def auto_desc(wikidata_entitie, type_text="long"):
    URL = "http://127.0.0.1:3000/?q="+wikidata_entitie+"&lang=fr&mode="+type_text+"&links=text&redlinks=&format=json&get_infobox=yes&infobox_template="
    #PARAMS = {'q': 213163, 'lang':'fr', 'mode':'long', 'links':'text', 'redlinks':'', 'format':'jsonfm', 'get_infobox':'yes', 'infobox_template':''}
    r = requests.get(url=URL)
    #dp1.write_json(r.json(), file_folder + "Process_data/Dictionary_approach/" + "test_autodesc.json")
    #x = r.json()["result"].replace('<b>', '').replace('</b>', '').replace('<br/>', '').replace('<br>', '').replace('\n', '')
    return r.json()["label"], r.json()["manual_description"], r.json()["result"]



'''with open(file_folder + "Process_data/Dictionary_approach/" + "vocabulaire.txt", 'r') as file:
  document = file.readlines()
  dict_vocab = []

  for s in document:
      dict_vocab.append({"name": s.split(" : ")[0].strip(), "wikidata_id": s.split(" : ")[1].strip()[-6:].replace(")", "")})
  dp1.write_json(dict_vocab, file_folder + "Process_data/Dictionary_approach/" + "dict_vocabulaire.txt")
  print(dict_vocab)
'''
'''with open(file_folder + "Process_data/Dictionary_approach/" + "vocabulaire.txt", "r") as text_file:
    for s in lst_all_sentence:
        text_file.write(s + "\n")'''


def get_wikidata_entities():
    with open(file_folder + "Process_data/Dictionary_approach/" + "dict_vocabulaire.json") as json_file:
        dict_vocabulaire = json.load(json_file)
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        dict_vocabulaire_entities = []
        for dict_voc in dict_vocabulaire:
            wikidata_id = dict_voc["wikidata_id"]

            sparql.setQuery("""
            SELECT ?item
            WHERE 
            {
              ?item wdt:""" + wikidata_id + """ ?o.
              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],fr". }
            }
            """)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            lres = results["results"]["bindings"]
            lst_entities = []
            for r in lres:
                lst_entities.append(r["item"]["value"])

            dict_vocabulaire_entities.append({
                "name": dict_voc["name"],
                "wikidata_id": wikidata_id,
                "entities": lst_entities,
            }
            )
            print("Current entitie => " + dict_voc["name"] + " number find = "+ str(len(lst_entities)))
        dp1.write_json(dict_vocabulaire_entities,
                       file_folder + "Process_data/Dictionary_approach/" + "dict_vocabulaire_entities.json")

    print("End function")


def get_texte_entities():
    with open(file_folder + "Process_data/Dictionary_approach/" + "dict_vocabulaire_entities.json") as json_file:
        dict_vocabulaire_entities = json.load(json_file)
        len_pref = len("http://www.wikidata.org/entity/Q")
        lst_all_auto_desc_text = []
        for dict_voc in dict_vocabulaire_entities:
            lst_entities = dict_voc["entities"]
            total = len(lst_entities)
            print("Current entitie => " + dict_voc["name"] + " number find = " + str(len(lst_entities)))
            auto_desc_text = ""
            percent = 0
            for entitie in lst_entities:
                percent += 1
                label, manual_description, auto_desc_text = auto_desc(wikidata_entitie=entitie[len_pref:], type_text="long")
                if not auto_desc_text:
                    label, manual_description, auto_desc_text = auto_desc(wikidata_entitie=entitie[len_pref:],
                                                                  type_text="short")
                lst_all_auto_desc_text.append({
                "voc_wikidata_id": dict_voc["wikidata_id"],
                "entitie_wikidata_id": entitie[len_pref-1:],
                "label": label,
                "manual_description": manual_description,
                "auto_desc_text": auto_desc_text
                })
                print("{:.2f} percent completed for entitie {}".format((percent/total)*100, entitie))
                #print(lst_all_auto_desc_text)
                #break
            #break
        dp1.write_json(lst_all_auto_desc_text,
                       file_folder + "Process_data/Dictionary_approach/" + "entities_auto_desc_text.json")

    print("End function")

get_texte_entities()

#get_wikidata_entities()
#test_requests()
#clean_expo_data()
#print(detect("Bonjour Monsieur"))
#process_train_data3()