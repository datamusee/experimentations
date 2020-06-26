import nltk
import json
import re
import pickle
import os
import string
#from SPARQLWrapper import SPARQLWrapper, POST, DIGEST

'''Sauvegarde les donnees json 
Arguments: donnees a sauvegarder et le nom du fichier
Returns:   None'''
def write_json(data, filename):
    if os.path.isfile(filename):
        open(filename, 'w').close()  # Suppression du contenu avant ecriture
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


'''Supprime la liste des doublons dans les styles artistiques et des caracteres speciaux 
Arguments: liste artistiques
Returns:   liste artistique clean'''
def clean_list(list_artistique):
    clean_art_list = []
    for art in list_artistique:
        art = re.sub(r'[()]', '', art)  # Suppression des parentheses
        art = art.strip()
        art = re.sub(r'[,]', '', art)  # suppression des virgules
        art = art.strip()
        if len(art) > 1 and (art not in clean_art_list):
            clean_art_list.append(art)

    return clean_art_list


file_folder = "/media/basile/New Volume/IFI/Stage/datasets/DataMusee/NER/"

'''Construit le fichier des styles artistiques 
Arguments: None
Returns:   None'''
def process_styles_artistiques_data():
    print("Start of process styles artistiques data")
    print("*" * 75)
    # file_folder = "/media/basile/New Volume/IFI/Stage/datasets/DataMusee/NER/"
    files = ["joconde-MUSEES-domaines-compte.json", "joconde-MUSEES-epoques-compte.json",
             "joconde-MUSEES-localisations-compte.json", "joconde-MUSEES-periodes-compte.json",
             "joconde-MUSEES-techniques-compte.json"]
    all_obj = []
    print("Start of process domaines data")
    with open(file_folder + files[0]) as json_file:
        data = json.load(json_file)
        lstArtistique = []
        for p in data:
            p = p.replace("(?)", "")
            p = p.replace("?", "").replace(")", "").replace("(", "")
            p = p.strip()
            if len(p) > 1 and (p not in lstArtistique):
                lstArtistique.append(p)
            # Fin traitement domaines
        all_obj.append(clean_list(lstArtistique))

    print("End of process domaines data")
    print("-" * 50)
    print("Start of process epoques data")
    with open(file_folder + files[1]) as json_file:
        data = json.load(json_file)
        lstArtistique = []
        no_mean_words = ["(?)", "(début)", "(fin)", "(début, ?)", "(fin, ?)"]
        for p in data:
            for no_mean_word in no_mean_words:
                p = p.replace(no_mean_word, "")
                p = p.strip()
            p_split = p.split('(')
            for pi in p_split:
                pi_strip = pi.replace("?", "").replace(")", "").replace("(", "")
                pi_strip = pi_strip.strip()
                if len(pi_strip) > 1 and (pi_strip not in lstArtistique):
                    lstArtistique.append(pi_strip)
            # Fin traitement epoques
        all_obj.append(clean_list(lstArtistique))

    print("End of process epoques data")
    print("-" * 50)
    print("Start of process localisations data")
    with open(file_folder + files[2]) as json_file:
        data = json.load(json_file)
        lstArtistique = []
        for p in data:
            p = p.replace("(?)", "")
            p = p.strip()
            p_split = p.split(';')
            for pi in p_split:
                pi_strip = pi.replace("?", "").replace(")", "").replace("(", "")  # strip()
                pi_strip = pi_strip.strip()
                if len(pi_strip) > 1 and (pi_strip not in lstArtistique):
                    lstArtistique.append(pi_strip)
            # Fin traitement localisations
        all_obj.append(clean_list(lstArtistique))

    print("End of process localisations data")
    print("-" * 50)
    print("Start of process periodes data")
    with open(file_folder + files[3]) as json_file:
        data = json.load(json_file)
        lstArtistique = []
        for p in data:
            p = p.replace("(?)", "")
            p = p.replace("?", "").replace(")", "").replace("(", "")
            p = p.strip()
            if len(p) > 1 and (p not in lstArtistique):
                lstArtistique.append(p)
            # Fin traitement periodes
        all_obj.append(clean_list(lstArtistique))

    print("End of process periodes data")

    print("-" * 50)
    print("Start of process techniques data")
    with open(file_folder + files[4]) as json_file:
        data = json.load(json_file)
        lstArtistique = []
        for p in data:
            p = p.replace("(?)", "")
            p_split = p.split('(')
            if len(p_split) < 2 and len(p_split[0].strip()) > 1 and (p_split[0].strip() not in lstArtistique):
                lstArtistique.append(p_split[0].strip())
            else:
                for pi in p_split[1:]:
                    pi_strip = pi.replace("?", "").replace(")", "").replace("(", "")
                    pi_strip = pi_strip.strip()
                    pi_strip_split = pi_strip.split(',')
                    for one_pi_strip_split in pi_strip_split:
                        one_pi_strip_split = one_pi_strip_split.replace("?", "").replace(")", "").replace("(", "")
                        one_pi_strip_split = one_pi_strip_split.strip()
                        if one_pi_strip_split:
                            one_technique = p_split[0].strip() + " " + one_pi_strip_split.strip()
                            if len(one_technique) > 1 and (one_technique not in lstArtistique):
                                lstArtistique.append(one_technique.strip())

                if len(p_split[0].strip().split()) > 1 and (p_split[0].strip() not in lstArtistique):
                    lstArtistique.append(p_split[0].strip())
                # Fin traitement techniques
        all_obj.append(clean_list(lstArtistique))
        print("End of process techniques data")
        print("-" * 50)
    data_dict = {}
    data_dict['DOMAINE'] = []
    data_dict['DOMAINE'].extend(all_obj[0])
    data_dict['EPOQUE'] = []
    data_dict['EPOQUE'].extend(all_obj[1])
    data_dict['LOCALISATION'] = []
    data_dict['LOCALISATION'].extend(all_obj[2])
    data_dict['PERIODE'] = []
    data_dict['PERIODE'].extend(all_obj[3])
    data_dict['TECHNIQUE'] = []
    data_dict['TECHNIQUE'].extend(all_obj[4])
    write_json(data_dict, file_folder + "styles_artistiques.json")

    print("Result file save in " + file_folder + "styles_artistiques.json")
    print("End of process styles artistiques data")
    print("*" * 75)


'''Construit le fichier des donnees des descriptions d'expositions artistiques 
Arguments: None
Returns:   None'''
def process_expositions_data():
    with open(file_folder + "Expo_comments.json") as json_file:
        data = json.load(json_file)
        results = (data["results"])["bindings"]
        # print(type(results))
        # print(results)
        cpt = 0
        nb_sent = 0
        open(file_folder + "tmp_expo.txt", 'w').close()  # Suppression du contenu du fichier avt ecriture
        for binding in results:
            cpt += 1
            cmt = binding["cmt"]
            if cmt["xml:lang"] == "fr":
                cmt_txt = cmt["value"]  # .replace('\n', '')
                with open(file_folder + "tmp_expo.txt", "a") as text_file:
                    text_file.write(cmt_txt)

        open(file_folder + "expo.txt", 'w').close()  # Suppression du contenu du fichier avt ecriture
        with open(file_folder + "tmp_expo.txt", 'r') as file:
            document = file.read().replace('\n', '')
            sentences_list = nltk.tokenize.sent_tokenize(document)
            for s in sentences_list:
                s = s.strip()
                if s:
                    nb_sent += 1
                    with open(file_folder + "expo.txt", "a") as text_file:
                        text_file.write(s + "\n")
        #print(cpt)
        #print(nb_sent)


'''Verifie si deux intervalles overlaps 
Arguments: deux intervalles a et b
Returns:   0 si non et la distance de overlaps si oui'''
def getOverlap(a, b):
    return max(0, min(a[1], b[1]) - max(a[0], b[0]))


'''Supprimer les overlaps dans les entites extraites 
Arguments: liste des entites extraites
Returns:   liste des entites extrites sans overlaps'''
def clean_overlaps_entities(list_entities):
    if len(list_entities) < 2:
        return list_entities

    clean_list_entities = []
    clean_list_entities.append(list_entities[0])
    del list_entities[0]
    for ent in list_entities:
        insert = False
        over_nothing = True
        list_a_remove = []
        for clean_ent in clean_list_entities:
            overlap = getOverlap([ent[0], ent[1]], [clean_ent[0], clean_ent[1]])
            if overlap > 0:
                over_nothing = False
                if ent[1] - ent[0] <= clean_ent[1] - clean_ent[0]:
                    break
                else:
                    list_a_remove.append(clean_ent)  # Enregistrer les element a supprimer
                    insert = True

        for rm_ent in list_a_remove:
            clean_list_entities.remove(rm_ent)

        if insert:
            clean_list_entities.append(ent)
        elif over_nothing and not insert:
            clean_list_entities.append(ent)

    return clean_list_entities

'''Crée le Train data de format texte et liste des entite aux positions corespondantes 
Arguments: None
Returns:   Train Data'''
def process_train_data():
    with open(file_folder + "styles_artistiques.json") as json_file:
        data = json.load(json_file)
        # lstArtistique = []
    with open(file_folder + "expo.txt", 'r') as file:
        document = file.readlines()

    train_data = []
    invalid_caracters = list(set(string.punctuation))
    invalid_caracters.insert(0, " ")

    for s in document:
        s = s.replace('\n', '')
        # chercher les techniques dans s
        lst_entities = []
        for p in data:
            # print(p) #p = DOMAINE, EPOQUE, LOCALISATION, PERIODE, TECHNIQUE
            # print(data[p]) # data[p] = list des p
            words = data[p]
            for w in words:
                # print(p+" => "+w)
                w = w.replace("?", "").replace(")", "").replace("(", "").replace(".", "")
                w = w.strip()
                if w:
                    for match in re.finditer(w, s):
                        # print("match found from {} to {}".format(match.start(), match.end()))
                        if match.start() == 0:
                            if s[match.end()] in invalid_caracters:
                                print(w + " => " + s)
                                lst_entities.append((match.start(), match.end(), p))
                        elif s[match.start() - 1] in invalid_caracters and s[match.end()] in invalid_caracters:
                            print(w + " => " + s)
                            lst_entities.append((match.start(), match.end(), p))

        lst_entities = clean_overlaps_entities(lst_entities)#Supprimer les overlaps entre les entites
        print(lst_entities)
        train_data.append((s, {"entities": lst_entities}))

    write_json(train_data, file_folder + "train_data.json")

    with open(file_folder + "train_data.pickle", 'wb') as handle:
        pickle.dump(train_data, handle)
    # with open(file_folder + "train_data.pickle", 'rb') as handle:
    #    train_data = pickle.load(handle)

    # print(document)


# process_styles_artistiques_data()
#process_train_data()

#sparql = SPARQLWrapper("https://ws49-cl4-jena.tl.teralab-datascience.fr/dmexpo/query")

