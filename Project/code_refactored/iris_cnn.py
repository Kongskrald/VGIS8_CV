from __future__ import print_function
import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
import os
import random as rd
from keras.preprocessing.image import ImageDataGenerator
import imagePatchGenerator5_module as patchGen
import general_cnn_functions as general_cnn
import fusion_data_creater as chimerc_data_module
from sklearn.utils import shuffle
import datetime
rd.seed(42)

#%%
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
import numpy as np
from sklearn.model_selection import train_test_split

from numpy import array
from numpy import argmax
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

import cv2
'''
This module makes an iris cnn and trains is using pythonDatabase as a database.
functionality:
    loadIrisDatabase() = Loads the database and discards
    resizeImagesToArray(database) = resizes images to the wanted size
    exploreData(data,label_in) = used to plot the first data points
    makePatches(dataframe,labels,PlotPatches=False) = makes 5 image patches from 1 image
    onehotEncodingLabels(labels) = performs one hot encoding
    splitDataFromDatabase() = splits the data into training, validation and testing.
    
'''

#dataFrame = pd.read_pickle("pythonDatabase")
#dataFrame = shuffle(dataFrame)

def checkIfpandas(data):
    if (isinstance(data,type(pd.DataFrame()))==True):
        pass
    else:
        raise Exception('dataFrame is not a pandas dataframe')    

def loadIrisDatabase():
    '''
    Loads the database pythonDatabase from the folder that the script is in that contains the normalised iris iamges.
    Classes with less than 10 images are discarded.
    
    output:
        dataFrame = The database with dropped images as a Pandas dataframe
        label = The labels extracted from dataFrame in a list type
    
    '''

    # Comment this part in to use the data before the merger
    # Dropping classes with less than 10 images
    try:
        dataFrame = pd.read_pickle("pythonDatabase") 
    except Exception as e:
        #raise SystemExit(0)
        raise Exception('Could not locate pythonDatabase. Check folder if it is there')
    
    checkIfpandas(dataFrame)
    
    dataFrame = shuffle(dataFrame)
    counts = Counter(dataFrame.label)
    discardList = []
    minNumOfImages = 10
    for iris_name,value in counts.items():
        if value<minNumOfImages:
            discardList.append(iris_name)
    dataFrame = dataFrame[~dataFrame['label'].isin(discardList)]
    print("Classes' with less than %.f images discarded in total are %.f : " % (minNumOfImages,len(discardList)),discardList)
    label = dataFrame.label
    label = label.tolist() # The list coming from dataFrame is already in the correct format.
    return dataFrame, label

def loadChimericDatabase():
    '''
    loads the chimeric database from the chimeric database module
    output:
        chimeric_database = the chimeric database containing the iris, face, and labels
    '''
    chimeric_database = chimerc_data_module.getChimericDatabase()
    return chimeric_database

def extractIrisFromChimeric():
    '''
    extracts the iris part of the chimeric database and renames it to fit the iris panda frame
    
    output:
        chimeric_iris_only = panda dataframe containing iris images from the chimeric database and their corresponding iris label
    '''
    chimeric_database = loadChimericDatabase()
    chimeric_iris_only = pd.DataFrame({'image':chimeric_database['iris_image'],'label':chimeric_database['iris_label']})
    return chimeric_iris_only

def chimericLoadDataAndLabels():
    '''
    Gets the chimeric database base and returns it into variables that the other iris methods use.
    
    output:
        dataFrame = The database with iris images and labels from the chimeric database
        label = The labels extracted from dataFrame in a list type
        
    '''
    dataFrame = extractIrisFromChimeric()
    label = dataFrame.label
    label = label.tolist() # The list coming from dataFrame is already in the correct format.
    return dataFrame, label

def resizeImagesToArray(database):
    '''
    Resizes the images from a Pandas array to a numpy array.
    
    output:
        imageVector = the images from the Pandas dataframe as a numpy array.
    '''

    dataFrame = database    
    checkIfpandas(dataFrame)
    temp_for_reshape = dataFrame.image.values
    img_dim = temp_for_reshape[1].shape
    imageVector = []
    
    for i in temp_for_reshape:
        imageVector.append(np.array(i.reshape(img_dim)))
    imageVector = np.asarray(imageVector)
    return imageVector


def exploreData(data,label_in):
    '''
    This plots the data and prints the dimensions of the dataset.
    input:
        data = the images as a numpy array.
        label_in = the labels in a list type
    '''
    imageVector = data
    label = label_in
    if type(imageVector) is np.ndarray:
        pass
    else:
        raise Exception('imageVector is not a numpy array')
    
    if type(label) is list:
        pass
    else:
        raise Exception("label is not a list")
        

    print('Training data shape : ', imageVector.shape)
    uniqueClasses=np.unique(label)
    NuniqueClasses=len(uniqueClasses)
    print("Number of classes: ",NuniqueClasses)
    
    plt.figure(figsize=[8,imageVector.shape[1]])
    
    plt.subplot(121)
    plt.imshow(imageVector[0,:,:], cmap='gray')
    plt.title("Ground Truth : {}".format(label[0]))



def splitDataFromDatabase(dataFrame,label, Test_size = 0.2):
    '''
    This gets the data from the pythonDatabase, performs the nesecary operations and splits it.
    It returns train and validation data
    '''
    #dataFrame, label = loadIrisDatabase()
    imageVector = resizeImagesToArray(dataFrame)
    exploreData(imageVector,label)
    imageVector, label = general_cnn.makePatches(dataFrame,label)
    label_onehot = general_cnn.onehotEncodingLabels(label)
    
    NuniqueClasses = len(np.unique(label))
    print('Number of classes:', NuniqueClasses)

    train_X,valid_X,train_label,valid_label = train_test_split(imageVector, label_onehot, test_size=Test_size, random_state=13)
    return train_X,valid_X,train_label,valid_label,NuniqueClasses



def valFromTestSplit(Test_X,Test_label,Test_size = 0.5):
	test_X,valid_X,test_label,valid_label = train_test_split(Test_X, Test_label,stratify = Test_label,test_size=Test_size, random_state=13)
	return test_X,valid_X,test_label,valid_label

def createIrisCnnArchitecture(train_data,number_of_classes):
    '''
    This creates the model for CNN for iris recognition. To remove the outer layer model.layers.pop() can be used 
    input:
        train_data = the training data. Used to get the shape of the data for the input layer
        number_of_classes = the number of classes for classification used for the last layer  layer
    
    output:
        model= the architecture of the iris CNN model.
    '''
    input_shape = train_data[0].shape
    num_classes = number_of_classes
    
    from keras.models import Model
    from keras.layers import Input
    
    iris_model_in = Input(shape = input_shape)
    conv1 = Conv2D(6, kernel_size=(3, 3),
                     activation='relu',
                     input_shape=input_shape,
                     data_format='channels_first',
                     padding = "same",
                     name = 'iris_conv1')(iris_model_in)
    
    max1 = MaxPooling2D(pool_size=(2, 2),data_format='channels_first',
                     name = 'iris_max1')(conv1)
    
    conv2 = Conv2D(32,
                     kernel_size=(5, 5),
                     activation='relu',
                     padding = "same",
                     data_format='channels_first',
                     name = 'iris_conv2')(max1)
    
    max2 = MaxPooling2D(pool_size=(2, 2),data_format='channels_first',
                     name = 'iris_max2')(conv2)
    
    conv3 = Conv2D(64,
                     kernel_size=(5, 5),
                     activation='relu',
                     padding = "same",
                     data_format='channels_first',
                     name = 'iris_conv3')(max2)
    
    max3 = MaxPooling2D(pool_size=(2, 2),data_format='channels_first',
                     name = 'iris_max3')(conv3)
    
    conv4 = Conv2D(256,
                     kernel_size=(5, 5),
                     activation='relu',
                     padding = "same",
                     data_format='channels_first',
                     name = 'iris_conv4')(max3)
    
    
    flat = Flatten()(conv4)
    dense1 = Dense(1024, activation='relu',
                     name = 'iris_fc1')(flat)
    drop1 = Dropout(0.5)(dense1)
    dense2 = Dense(1024, activation='relu',
                     name = 'iris_fc2')(drop1)
    drop2 = Dropout(0.5)(dense2)
    
    iris_out = Dense(num_classes, activation='softmax',
                     name = 'iris_classification')(drop2)
    model = Model(iris_model_in,iris_out)
    return model


def NineNineIrisAcc():
    '''
    The settingts to get 99% accuracy with iris cnn with using a 0.2 validation split. The training split is by default 0.2.
    '''
    dataFrame, label = loadIrisDatabase()
    train_X,test_X,train_label,test_label,NuniqueClasses = splitDataFromDatabase(dataFrame, label)
    model = createIrisCnnArchitecture(train_X,NuniqueClasses)
    model,history = general_cnn.trainModelValsplit(model,train_X,train_label,Batch_size = 128,Epoch = 50,Learningrate = 1e-2)
    score = general_cnn.evaluateModel(model,test_X,test_label)
    plt_acc,plt_val = general_cnn.plotHistory(history)
    general_cnn.saveModel(model,score,plt_acc,plt_val,Model_name='iris_cnn')

def ValSplitIrisAcc():
    '''
    The settings to get 99% with using validation and test data from a real split. The training data is 0.6 and the test validation is 50/50
    '''
    dataFrame, label = loadIrisDatabase()
    train_X,test_X,train_label,test_label,NuniqueClasses = splitDataFromDatabase(dataFrame, label,Test_size = 0.4)
    test_X,valid_X,test_label,valid_label = valFromTestSplit(test_X,test_label,Test_size = 0.5)
    model = createIrisCnnArchitecture(train_X,NuniqueClasses)
    model,history = general_cnn.trainModelWithVal(model,train_X,train_label,valid_X,valid_label,Batch_size = 128,Epoch = 50,Learningrate = 1e-2)
    score = general_cnn.evaluateModel(model,test_X,test_label)
    plt_acc,plt_val = general_cnn.plotHistory(history)
    general_cnn.saveModel(model,score,plt_acc,plt_val,Model_name='iris_cnn')
    
def ChimericIrisAcc():
    '''
    This setting got 99.43 test accuracy using vadlidation and test data from chimeric data set. The training data is 0.6 and the test validation is 50/50
    '''
    dataFrame, label = chimericLoadDataAndLabels()
    train_X,test_X,train_label,test_label,NuniqueClasses = splitDataFromDatabase(dataFrame, label,Test_size = 0.4)
    test_X,valid_X,test_label,valid_label = valFromTestSplit(test_X,test_label,Test_size = 0.5)
    model = createIrisCnnArchitecture(train_X,NuniqueClasses)
    model,history = general_cnn.trainModelWithVal(model,train_X,train_label,valid_X,valid_label,Batch_size = 128,Epoch = 50,Learningrate = 1e-2)
    score = general_cnn.evaluateModel(model,test_X,test_label)
    plt_acc,plt_val = general_cnn.plotHistory(history)
    general_cnn.saveModel(model,score,plt_acc,plt_val,Model_name='chimeric_iris_cnn')
    
if __name__ == '__main__':
    #ValSplitIrisAcc()
    ChimericIrisAcc()

    pass