# Key Segmentation

Implementation for my M.S. thesis, "A Set of Rule-Based Approaches to Key Identification: Towards Improved Handling of Ambiguity and Subjectivity in Music."

### Thesis Abstract:
Music theoretic constructs such as tonality, harmony, and voice leading are often expressed ambiguously in music, yet the vast majority of datasets and music information retrieval systems attempt to create analyses that completely cover all musical input. Furthermore, most datasets encode a single analysis, even though the perception of the corresponding musical constructs may differ significantly among listeners, depending on individual differences such as musical sophistication and listening histories. In this thesis, an approach to key segmentation is introduced that handles music’s inherent ambiguity and listener subjectivity in a feasible way through rule-based partial analyses and multiple annotations, each mapping to a different, prototypical reference listener. These partial analyses are implemented using the chord and key label outputs of an existing state-of-the- art key segmentation model. Experimental evaluations show that partial analyses that are associated with unambiguous, clear key definitions lead to higher accuracy. Additionally, evaluating on partial analyses that this model predicts with high confidence leads to higher precision without a decrease in recall. The proposed approach to musical ambiguity and listener subjectivity is expected to be applicable to other music analysis tasks, with potential improvements in the performance of music information retrieval pipelines.

### Instructions to Run Code:
#### Install Conda Environment:
```
conda env create -f environment.yml
conda activate key-segmentation
```

#### Recreate Thesis Results:
##### Recreate Table 6.1 (Clear Key Segment) Results:
```
cd src/accuracy_computer
./clear_key_segment_results_computer.sh
```

##### Recreate Table 6.2 (Thresholded Frog Model) Results:
```
cd src/accuracy_computer
./thresholded_micchi_model.sh
```

##### Recreate Tables 6.3 and 6.4 (Fragmentation) Results:
```
cd src/accuracy_computer

# Table 6.3:
./clear_key_segment_fragmentation_computer.sh

# Table 6.4:
./thresholded_micchi_model.sh
```

##### Recreate Tables 6.5-6.8 (Whole Key Segment) Results:
```
# Table 6.5:
./whole_clear_key_segment_results_computer.sh

# Tables 6.6:
./thresholded_micchi_model.sh

# Table 6.7:
./whole_clear_key_segment_fragmentation_computer.sh

# Table 6.8:
./thresholded_micchi_model.sh
```

##### Recreate Clear Thresholded Key Segment Precision and Recall Plots in Figures 6.1-6.6:
```
cd src/accuracy_computer
./whole_key_segment_stats_plotter.sh
```

#### Extract Key Segments:
```
```