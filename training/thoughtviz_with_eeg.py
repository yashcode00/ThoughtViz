import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1,"/Users/yash/Desktop/ADL-Project/ThoughtViz")
import os
import pickle
import random
from PIL import Image
from keras import backend as K
from keras.models import load_model
from keras.optimizers import Adam
from keras.utils import to_categorical

import utils.data_input_util as inutil
from training.models.thoughtviz import *
from utils.image_utils import * 


def train_gan(dataset, input_noise_dim, batch_size, epochs, data_dir, saved_classifier_model_file, model_save_dir, output_dir, classifier_model_file):

    K.set_learning_phase(False)
    # folders containing images used for training
    char_fonts_folders = ["/Users/yash/Desktop/ADL-Project/ThoughtViz/training/images/Char-Font"]
    num_classes = 10
    img_input_shape = (64,64)

    feature_encoding_dim = 100

    # load data and compile discriminator, generator models depending on the dataaset
    if dataset == 0:
        x_train, y_train, x_test, y_test = inutil.load_digit_data()
        print("Loaded Digits Dataset.", )

    if dataset == 1:
        x_train, y_train, x_test, y_test = inutil.load_char_data(char_fonts_folders, resize_shape=(28, 28))
        print("Loaded Characters Dataset.", )
    
    if dataset == 2:
        imagenet_dir = "/Users/yash/Desktop/ADL-Project/ThoughtViz/training/images/ImageNet-Filtered"
        x_train, y_train, x_test, y_test = inutil.load_image_data(imagenet_folder=imagenet_dir, patch_size=img_input_shape)

    print(f"Shape of inputs is {x_train.shape}")

    adam_lr = 0.00005
    adam_beta_1 = 0.5

    c = load_model(classifier_model_file)

    d = discriminator_model(img_input_shape, c)
    d_optim = Adam(lr=adam_lr, beta_1=adam_beta_1)
    d.compile(loss=['binary_crossentropy','categorical_crossentropy'], optimizer=d_optim)
    d.trainable = True

    g = generator_model(input_noise_dim, feature_encoding_dim)
    g_optim = Adam(lr=adam_lr, beta_1=adam_beta_1)
    g.compile(loss='categorical_crossentropy', optimizer=g_optim)

    d_on_g = generator_containing_discriminator(input_noise_dim, feature_encoding_dim, g, d)
    d_on_g.compile(loss=['binary_crossentropy','categorical_crossentropy'], optimizer=g_optim)

    g.summary()
    d.summary()
    
    eeg_data = pickle.load(open(os.path.join(data_dir, 'data.pkl'), "rb"), encoding='latin1')
    # print(eeg_data)
    classifier = load_model(saved_classifier_model_file)
    classifier.summary()
    x_test = eeg_data['x_test']
    y_test = eeg_data['y_test']
    y_test = [np.argmax(y) for y in y_test]
    layer_index = 9

    # keras way of getting the output from an intermediate layer
    get_nth_layer_output = K.function([classifier.layers[0].input], [classifier.layers[layer_index].output])

    layer_output = get_nth_layer_output([x_test])[0]

    for epoch in range(epochs):
        print("Epoch is ", epoch)

        print("Number of batches", int(x_train.shape[0]/batch_size))

        for index in range(int(x_train.shape[0]/batch_size)):
            # generate noise from a normal distribution
            noise = np.random.uniform(-1, 1, (batch_size, input_noise_dim))

            random_labels = np.random.randint(0, 10, batch_size)

            one_hot_vectors = [to_categorical(label, 10) for label in random_labels]
            
            eeg_feature_vectors = np.array([layer_output[random.choice(np.where(y_test == random_label)[0])] for random_label in random_labels])

            # get real images and corresponding labels
            real_images = x_train[index * batch_size:(index + 1) * batch_size]
            real_labels = y_train[index * batch_size:(index + 1) * batch_size]

            # generate fake images using the generator
            generated_images = g.predict([noise, eeg_feature_vectors], verbose=0)

            # discriminator loss of real images
            d_loss_real = d.train_on_batch(real_images, [np.array([1] * batch_size), np.array(real_labels)])
            # discriminator loss of fake images
            d_loss_fake = d.train_on_batch(generated_images, [np.array([0] * batch_size), np.array(one_hot_vectors).reshape(batch_size, num_classes)])
            d_loss = (d_loss_fake[0] + d_loss_real[0]) * 0.5

            # save generated images at intermediate stages of training
            if index % 250 == 0:
                image = combine_images(generated_images)
                image = image * 127.5 + 127.5
                img_save_path = os.path.join(output_dir, str(epoch) + "_g_" + str(index) + ".png")
                Image.fromarray(image.astype(np.uint8)).save(img_save_path)

            d.trainable = False
            # generator loss
            g_loss = d_on_g.train_on_batch([noise, eeg_feature_vectors], [np.array([1] * batch_size), np.array(one_hot_vectors).reshape(batch_size, num_classes)])
            d.trainable = True

        print("Epoch %d d_loss : %f" % (epoch, d_loss))
        print("Epoch %d g_loss : %f" % (epoch, g_loss[0]))

        # save generator and discriminator models along with the weights
        g.save(os.path.join(model_save_dir, 'generator_' + str(epoch)), overwrite=True, include_optimizer=True)
        d.save(os.path.join(model_save_dir, 'discriminator_' + str(epoch)), overwrite=True, include_optimizer=True)


def train():
    folder_name_mapping = {0: 'Digit', 1: 'Char', 2:'Image'}
    dataset = 2
    batch_size = 100
    run_id = 1
    epochs = 500
    model_save_dir = os.path.join('./saved_models/thoughtviz_with_eeg/', folder_name_mapping[dataset], 'run_' + str(run_id))
    if not os.path.exists(model_save_dir):
        os.makedirs(model_save_dir)

    output_dir = os.path.join('./outputs/thoughtviz_with_eeg/', folder_name_mapping[dataset], 'run_' + str(run_id))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    classifier_model_file = os.path.join('/Users/yash/Desktop/ADL-Project/ThoughtViz/training/models/trained_classifier_models', 'classifier_' + folder_name_mapping[dataset].lower() + '.h5')

    eeg_data_dir = os.path.join('/Users/yash/Desktop/ADL-Project/ThoughtViz/training/data/eeg', folder_name_mapping[dataset].lower())
    eeg_classifier_model_file = os.path.join('/Users/yash/Desktop/ADL-Project/ThoughtViz/training/models/eeg_models', folder_name_mapping[dataset].lower(), 'run_final.h5')


    eeg_data_dir = "/Users/yash/Desktop/ADL-Project/ThoughtViz/training/data/eeg/digit"

    train_gan(dataset=dataset, input_noise_dim=100, batch_size=batch_size, epochs=epochs, data_dir=eeg_data_dir, saved_classifier_model_file=eeg_classifier_model_file, model_save_dir=model_save_dir, output_dir=output_dir, classifier_model_file=classifier_model_file)


if __name__ == '__main__':
    train()
