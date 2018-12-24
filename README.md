# ThoughtViz
Implementation for the paper https://dl.acm.org/citation.cfm?doid=3240508.3240641

## EEG Data

* Download the EEG data from https://drive.google.com/open?id=1atP9CsjWIT-hg3fX--fcC1hg0uvg9bEH
* Extract it and place it in the project folder (.../ThoughtViz/data)

## Trained Models

* Download the trained EEG Classification from https://drive.google.com/open?id=1cq8RTBiwqO-Jo0TZjBNlRHZEhjKDknKP
* Extract them and place in the models folder (.../ThoughtViz/models/eeg_models)
* Download the trained image classifier models used in training from https://drive.google.com/open?id=1U9qtN1SlOS3dzd2BwWWHhJiMz_0yNW9U
* Extract them and place in the training folder (.../ThoughtViz/training/trained_classifier_models)

## Training

1. EEG Classification

2. GAN Training

## Testing

* Download the sample trained GAN models from https://drive.google.com/open?id=1uFFhvTsU2nmdaecR2WPWsiGJfgI3as1_
* Extract them and place in the models folder (.../ThoughtViz/models/gan_models)

* Run test.py to run the sample tests 

   1. Baseline Evaluation

      * DeLiGAN : Uses 1-hot class label as conditioning with MoGLayer at the input.

   2. Final Evaluation

      * Our Approach : Uses EEG encoding from the trained EEG classifier as conditioning. The encoding is used as weights in the MoGLayer
 
**NOTE** : Currently we have uploaded only one baseline model and our final model. Other models can be obtained by running the training code. 



