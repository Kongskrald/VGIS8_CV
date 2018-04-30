# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 10:58:23 2018

@author: Shaggy
"""

import h5py
import scipy as spy
import numpy as np
import math
import matplotlib.pyplot as plt

# Ignore warnings from sklearn because they fill up the console
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=UserWarning) 
#import tensorflow as tf
#from more_itertools import locate

def indices(lst, element):
    result = []
    offset = -1
    while True:
        try:
            offset = lst.index(element, offset+1)
        except ValueError:
            return result
        result.append(offset)



def genRand(min, max, sampleSize):
    answer=[]
    answerSize=0
    while answerSize < sampleSize:
        r = np.random.randint(min, max)
        if r not in answer:
            answerSize += 1
            answer.append(r)
    return answer


#load the data 



f = h5py.File('database_segmented.mat', 'r');
 
print("Keys: %s" % f.keys())
a_group_key = list(f.keys())[3]
featureVector = np.array(f[a_group_key])
featureVector = featureVector.transpose()
p=featureVector.shape
print(p)
#print(featureVector)
 
import csv
with open('label.csv', 'r') as f:
   reader = csv.reader(f)
   label = [row for row in reader]


#set general parameters

#k_fold_param=5
PPTrainSize=5 

#split data in train and validation sets

label_list = [item for sublist in label for item in sublist]#make a it flatlist
uniqueClasses=np.unique(label_list)
NuniqueClasses=len(uniqueClasses)

np.random.seed(42)

TrainData=np.empty((0,p[1]))
TrainIndices=[]
TrainLabel=[] 

for s in range(0,NuniqueClasses):
    globals()['ClassSamples%s' % s]=indices(label_list,uniqueClasses[s])
    globals()['Rand%s' % s]=genRand(0,len(eval('ClassSamples' + str(s))),PPTrainSize)

    for t in range(0, len(eval('Rand' + str(s)))):
        TrainIndices.append(eval('ClassSamples' + str(s))[eval('Rand' + str(s))[t]])
        TrainData=np.append(TrainData,[featureVector[eval('ClassSamples' + str(s))[eval('Rand' + str(s))[t]]]],axis=0)
        TrainLabel.append(label_list[eval('ClassSamples' + str(s))[eval('Rand' + str(s))[t]]])
ValiLabel=[]#Create a list for the labels of the validation samples
ValiData=np.empty((0,p[1]))#Create an array for the validation samples
AllI=np.arange(p[0])
ValidationIndices=np.setdiff1d(AllI,TrainIndices)#find all indices for the ones not in train set

for NValiSample in range(0,len(ValidationIndices)):
    ValiLabel.append(label_list[ValidationIndices[NValiSample]])
    ValiData=np.append(ValiData,[featureVector[ValidationIndices[NValiSample]]],axis=0)

print(AllI)
print(ValidationIndices)
print(TrainData.shape)
print(TrainIndices)
print(ValidationIndices)




'''
This part is about training and seeing how well the different classifiers
perform with k=5 K-fold cross validation. We use 20% of the data for training
'''
from sklearn.model_selection import KFold # import KFold
from sklearn import svm
from sklearn.model_selection import cross_val_score


kf = 5 #KFold(n_splits=5) # Define the split - into 5 folds
print("Performing",kf,"Kfold crossvalidation")
clf = svm.SVC(kernel='linear')
scores = cross_val_score(clf, TrainData, np.ravel(TrainLabel), cv=kf)
print("Accuracy for linear CV: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

clf2 = svm.SVC(kernel='poly')
scores2 = cross_val_score(clf2,TrainData, np.ravel(TrainLabel), cv=kf)
print("Accuracy for quadratic CV: %0.2f (+/- %0.2f)" % (scores2.mean(), scores2.std() * 2))

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
lda = LinearDiscriminantAnalysis()
scores3 = cross_val_score(lda, TrainData, np.ravel(TrainLabel), cv=kf)
print("Accuracy for LDA CV: %0.2f (+/- %0.2f)" % (scores3.mean(), scores3.std() * 2))

from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt
myList = list(range(1,25))
neighbors = list(filter(lambda x: x % 2 != 0, myList))
cv_scores = []
for k in neighbors:
    knn = KNeighborsClassifier(n_neighbors=k)
    scores = cross_val_score(knn,TrainData, np.ravel(TrainLabel), cv=kf, scoring='accuracy')
    cv_scores.append(scores.mean())
    
MSE = [1 - x for x in cv_scores]
optimal_k = neighbors[MSE.index(min(MSE))]
print ("The optimal number of neighbors is %d" % optimal_k)
plt.plot(neighbors, MSE)
plt.xlabel('Number of Neighbors K')
plt.ylabel('Misclassification Error')
plt.show()

knn2 = KNeighborsClassifier(n_neighbors=optimal_k)
scores4 = cross_val_score(knn2,TrainData, np.ravel(TrainLabel), cv=kf, scoring='accuracy')
print("Accuracy for KNN k =",optimal_k," CV: ",scores4.mean(), "+/-", scores4.std() * 2)

'''
Here we train the model with the 20% data and validate it on the rest of the 80% 
'''
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

size_of_train_for_model = 0.5
X_train, X_test, y_train, y_test = train_test_split(featureVector, label, train_size=size_of_train_for_model,stratify=label,random_state=42)
print("Amount of data being used training: ",size_of_train_for_model, "and", 1-size_of_train_for_model, "for validation")

clf_model = svm.SVC(kernel='linear').fit(X_train,np.ravel(y_train))
predicted_data = clf_model.predict(X_test)
print("Accuracy of validation on linear SVM: ",accuracy_score(y_test, predicted_data))


# This is to manually calcuate the accuracy instead of using the accuracy_score functionallity which does the same.
#PredictedClass_SVM=clf_model.predict(X_test) #classify using trained classifier
#PredictedClass_SVM = PredictedClass_SVM.reshape(PredictedClass_SVM.size,1)
#PredictionCorrectness_SVM=PredictedClass_SVM==y_test #compare to known labels
#SVM_accuracy=PredictionCorrectness_SVM.sum()/len(y_test)#calculate accuracy
#print('SVM accuracy:',SVM_accuracy)


clf2_model = svm.SVC(kernel='poly').fit(X_train,np.ravel(y_train))
print("Accuracy of validation on quadratic SVM: ",accuracy_score(y_test, clf2_model.predict(X_test)))

lda_model = LinearDiscriminantAnalysis().fit(X_train,np.ravel(y_train))
print("Accuracy of validation on LDA: ",accuracy_score(y_test, lda_model.predict(X_test)))

knn_model = KNeighborsClassifier(n_neighbors=optimal_k).fit(X_train,np.ravel(y_train))
print("Accuracy of validation on KNN k =",optimal_k,": ",accuracy_score(y_test, knn_model.predict(X_test)))
