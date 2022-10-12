# Key Segmentation

Implementation for my M.S. thesis, "A Set of Rule-Based Approaches to Key Identification: Towards Improved Handling of Ambiguity and Subjectivity in Music."

This project is licensed under the terms of the GNU GPLv3 license.

### Thesis Abstract:
Music theoretic constructs such as tonality, harmony, and voice leading are often expressed ambiguously in music, yet the vast majority of datasets and music information retrieval systems attempt to create analyses that completely cover all musical input. Furthermore, most datasets encode a single analysis, even though the perception of the corresponding musical constructs may differ significantly among listeners, depending on individual differences such as musical sophistication and listening histories. In this thesis, an approach to key segmentation is introduced that handles music’s inherent ambiguity and listener subjectivity in a feasible way through rule-based partial analyses and multiple annotations, each mapping to a different, prototypical reference listener. These partial analyses are implemented using the chord and key label outputs of an existing state-of-the- art key segmentation model. Experimental evaluations show that partial analyses that are associated with unambiguous, clear key definitions lead to higher accuracy. Additionally, evaluating on partial analyses that this model predicts with high confidence leads to higher precision without a decrease in recall. The proposed approach to musical ambiguity and listener subjectivity is expected to be applicable to other music analysis tasks, with potential improvements in the performance of music information retrieval pipelines.

### Instructions to Run Code:
#### Install Key Segmentation Conda Environment:
```
conda env create -f environment.yml
conda activate key-segmentation
```


#### Recreate Thesis Results:
##### Recreate Table 6.1 (Clear Key Segment) Results:
```
cd src/results_computation
./clear_key_segment_results_computer.sh
```

##### Recreate Table 6.2 (Thresholded Frog Model) Results:
```
cd src/results_computation
./thresholded_key_segment_results_computer.sh
```

##### Recreate Tables 6.3 and 6.4 (Fragmentation) Results:
```
cd src/results_computation

# Table 6.3:
./clear_key_segment_fragmentation_computer.sh

# Table 6.4:
./thresholded_key_segment_fragmentation_computer.sh
```

##### Recreate Tables 6.5-6.8 (Whole Key Segment) Results:
```
cd src/results_computation

# Table 6.5:
./whole_clear_key_segment_results_computer.sh

# Tables 6.6:
./whole_thresholded_key_segment_results_computer.sh

# Table 6.7:
./whole_clear_key_segment_fragmentation_computer.sh

# Table 6.8:
./whole_thresholded_key_segment_fragmentation_computer.sh
```

##### Recreate Clear Thresholded Key Segment Precision and Recall Plots in Figures 6.1-6.6:
```
# First uncomment the line for the clear key segment
# definition to use.
cd src/results_computation
./whole_key_segment_stats_plotter.sh
```

#### Extract Key Segments:

##### Extract Ground Truth Clear Key Segments from Meta-Corpus:
```
cd src/key_segment_definitions

# First uncomment the line for the clear key segment
# definition to use.
./ground_truth_key_segment_annotator_and_exporter.sh
```

##### Extract Clear Key Segments from Meta-Corpus Based on Frog Model Key and Chord Predictions:
```
cd src/key_segment_definitions

# First uncomment the line for the clear key segment
# definition to use.
./micchi_predictions_key_segment_annotator_and_exporter.sh
```

##### Extract Thresholded Key Segments from Meta-Corpus:
```
cd src/key_segment_definitions

# First uncomment the line for the clear key segment
# definition to use.
./thresholded_micchi_model_key_segment_annotator_and_exporter.sh
```

#### Install Frog Conda Environment:
Note that the only difference between this environment and the `key-segmentation` environment above is that the version of music21 required to run the Frog model is 6.5.0 (rather than 6.7.0 above). This environment should only be used when running code inside of the `src/frog` directory. At all other times, the `key-segmentation` environment should be used.
```
cd src/frog
conda env create -f environment.yml
```

#### Intermediate Files:
How to generate the input files used for the commandline arguments inside any of the above shell scripts:
* `--ground_truth_event_key_labels_npz_path`: This file contains the ground truth key label for each event inside each song to be evaluated on.
    ```
    cd src/results_computation
    ./micchi2021_csv_chords_2_event_key_labels_converter.sh
    ```
* `--pred_key_segment_boundaries_npz_path`: This contains the start and stop time in eighth note beat indices for each clear key segment for each song predicted by the Micchi model. Generated using the instructions for 'Extract Clear Key Segments from Meta-Corpus Based on Frog Model Key and Chord Predictions' above.
* `--ground_truth_key_segment_boundaries_npz_path`: This contains the start and stop time in eighth note beat indices for each clear key segment for each song identified using the ground truth chord and key labels. Generated using the instructions for 'Extract Ground Truth Clear Key Segments from Meta-Corpus' above.
* `--event_key_preds_npz_path`: This file contains the predicted key label for each event inside each song to be evaluated on.
    ```
    cd src/frog
    conda activate frog
    ./get_key_predictions.sh
    # Output .npz file will appear inside `out/` in a folder named with the
    # date/time that the script was ran.
    ```
* `--event_key_probs_npz_path`: This file contains the predicted key probabilities over the 24 keys for each event inside each song to be evaluated on.
    ```
    cd src/frog
    conda activate frog
    ./get_key_probabilities.sh
    # Output .npz file will appear inside `out/` in a folder named with the
    # date/time that the script was ran.
    ```
* `--predicted_rntxt_filepaths_dir`: This is the name of the folder inside `src/frog/out` that contains the predicted chord and key labels for each song. Inside the folder, there is a .rntxt file for each song. Instructions to generate the .rntxt prediction files are provided below:
    ```
    cd src/frog
    conda activate frog
    ./get_roman_numeral_analysis.sh
    # Output .rntxt files will appear inside `out/` in a folder named with the
    # date/time that the script was ran.
    ```

#### Retrain Frog Model:
```
cd src/frog
conda activate frog
./cra_train.sh
```