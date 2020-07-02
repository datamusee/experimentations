from sklearn.model_selection import train_test_split
import pickle
from sklearn.model_selection import KFold
import spacy
import random
import time
import numpy as np
from spacy.util import minibatch, compounding
from itertools import chain


# A simple decorator to log function processing time
def timer(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print("Completed in {} seconds".format(int(te - ts)))
        return result

    return timed


# Data must be of the form (sentence, {entities: [start, end, label]})

@timer
def train_spacy(train_data, iterations, dropout=0.2, display_freq=1):
    nlp = spacy.blank('en')
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)

    # Add entity labels to the NER pipeline

    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # Disable other pipelines in SpaCy to only train NER
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):
        nlp.vocab.vectors.name = 'spacy_model'  # without this, spaCy throws an "unnamed" error
        optimizer = nlp.begin_training()
        for itr in range(iterations):
            random.shuffle(train_data)  # shuffle the training data before each iteration
            losses = {}
            batches = minibatch(train_data, size=compounding(4., 32., 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,
                    annotations,
                    drop=dropout,
                    sgd=optimizer,
                    losses=losses)
            if itr % display_freq == 0:
                print("Iteration {} Loss: {}".format(itr + 1, losses))
    return nlp




def calc_precision(pred, true):
    precision = len([x for x in pred if x in true]) / (len(pred) + 1e-20) # true positives / total pred
    return precision

def calc_recall(pred, true):
    recall = len([x for x in true if x in pred]) / (len(true) + 1e-20)# true positives / total test
    return recall

def calc_f1(precision, recall):
    f1 = 2 * ((precision * recall) / (precision + recall + 1e-20))
    return f1

def cal_metrics(X):
    # run the predictions on each sentence in the test dataset, and return the spacy object
    preds = [ner(x[0]) for x in X]

    precisions, recalls, f1s = [], [], []

    # iterate over predictions and test data and calculate precision, recall, and F1-score
    for pred, true in zip(preds, X):
        true = [x[2] for x in
                list(chain.from_iterable(true[1].values()))]  # x[2] = annotation, true[1] = (start, end, annot)
        pred = [i.label_ for i in pred.ents]  # i.label_ = annotation label, pred.ents = list of annotations
        precision = calc_precision(true, pred)
        precisions.append(precision)
        recall = calc_recall(true, pred)
        recalls.append(recall)
        f1s.append(calc_f1(precision, recall))

    return np.around(np.mean(precisions), 3), np.around(np.mean(recalls), 3), np.around(np.mean(f1s), 3)



file_folder = "/media/basile/New Volume/IFI/Stage/datasets/DataMusee/NER/"

with open(file_folder + "Process_data/" + "train_data.pickle", 'rb') as handle:
    All_DATA = pickle.load(handle)

#TEST_SIZE = 0.1
#X_train, X_val = train_test_split(X, test_size = TEST_SIZE, shuffle=True, random_state=42)
#X_train, X_val = train_test_split(All_DATA, test_size = TEST_SIZE, shuffle=True, random_state=42)

#print("All data = "+str(len(All_DATA)) + " Train size = "+str(len(X_train)) + " Val size = "+str(len(X_val)))

# A simple decorator to log function processing time


nb_splits = 10
kf = KFold(n_splits=nb_splits)
kf.get_n_splits(All_DATA)
precisions_train, recalls_train, f1s_train = [], [], []
precisions_test, recalls_test, f1s_test = [], [], []
nb_iter = 0

for train_index, test_index in kf.split(All_DATA):
    nb_iter += 1
    print("*"*50)
    print("Start iteration "+str(nb_iter))
    X_train = [All_DATA[i] for i in train_index.tolist()]
    X_test = [All_DATA[i] for i in test_index.tolist()]
    print("All data = " + str(len(All_DATA)) + " Train size = " + str(len(X_train)) + " Val size = " + str(len(X_test)))
    # Train (and save) the NER model
    # add labels
    nb_interations = 50
    ner = train_spacy(X_train, nb_interations)
    ner.to_disk("ner_models/" + "/ner_spacy_" + str(nb_interations))

    p_train, r_train, f_train = cal_metrics(X_train)
    precisions_train.append(p_train)
    recalls_train.append(r_train)
    f1s_train.append(f_train)
    print("Train Metrics : ")
    print("Precision: {} \nRecall: {} \nF1-score: {}".format(p_train,
                                                             r_train,
                                                             f_train))
    p_test, r_test, f_test = cal_metrics(X_test)
    precisions_test.append(p_test)
    recalls_test.append(r_test)
    f1s_test.append(f_test)
    print("Test Metrics : ")
    print("Precision: {} \nRecall: {} \nF1-score: {}".format(p_test,
                                                             r_test,
                                                             f_test))
with open("metrics_"+str(nb_interations)+".txt", "a") as text_file:
    for p in range(nb_splits):
        for h in range(6):
            text_file.write(precisions_train[p][h] + "\n")
            text_file.write(recalls_train[p][h] + "\n")
            text_file.write(f1s_train[p][h] + "\n")
            text_file.write(precisions_test[p][h] + "\n")
            text_file.write(recalls_test[p][h] + "\n")
            text_file.write(f1s_test[p][h] + "\n")

print("_"*40)
print("End")
print("*"*50)
