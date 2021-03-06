This is a "READ ME" file for the report "Multimodal Biometric Identity Verification for Mobile Platforms" by VGIS group 18gr842
The zip-file contains scripts for iris segmentation, normalisation, feature extraction and categorisation used for a fusion net Convolutional Neural Network (CNN)
It is written in MATLAB 2017a and Pythin 3.6

Iris Segmentation and normalisation is done in MATLAB. To generate the files run miniproject.m .  It needs a folder called "warsaw" with the Warsaw-BioBase iris database and another called "diagnostics" in which it will put the processed iris images. Move processed images to the folder "normalised iris" once it is finished running. miniproject.m will also generate database.m .

To do iris classification with machine learning (KNN, LDA and SVM) run iris_classification.py . It loads pythonDatabase to get the iris data. If pythonDatabase is missing it can be generated by running main_script.py

To do iris cnn recognition run iris_cnn.py . It loads pythonDatabase to get the iris data. If pythonDatabase is missing it can be generated by running main_script.py . It can be run with both the chimeric data and the iris data before it has been merged. This can easily be configured by commenting out the chimeric part and commenting in the old data. The necessary parts to comment in and out are specified in iris_cnn.py .

To do face cnn recognition run VGG16_face_cnn.py . It will load the LFW database through Keras. As with iris_cnn.py it is possible to run with the chimeric data and with just the LFW data. The necessary comments and uncomments are specified in VGG16_face_cnn.py .

To do the merged iris and face with the fusion net run merged_iris_face_fusion_net.py .

Dependencies:
imagePatchGenerator5_module.py : This takes an image and generates 5 image patches. 
fusion_data_creater.py : This creates the chimeric database used for the fusion net in merged_iris_face_fusion_net.py .
iris_face_merge_cnn_data_splitter: This takes the chimeric data and splits it into training, validation and test set, which can be used as cnn inputs.
load_database.m : Loads the Warsaw-BioBase database into a MATLAB structure.
noiseremover_python.py: Removes the eyelashes from iris images and performs histogram equalisation (histogram stretching).
noiseremover.m : Does the same noise remover part of noiseremover_python.py just in MATLAB
equalisehistogram: Does histogram equalisation (histogram stretching) part of noiseremover_python.py just in MATLAB.
neweyelidsup.m : Does eyelid suppression in MATLAB.
cell2csv.m : converts MATLAB cells to csv format. Used to create the label.csv file that contains the labels of the normalised iris images.
Keras API on top of Tensorflow backend.

daugman folder: contains the library to perform daugmans integro-differential operator in MATLAB. It is used to locate the iris bounds.
libormasek folder: contains the libormasek library, which performs iris segmentation, eyelid suppression and normalisation. 


