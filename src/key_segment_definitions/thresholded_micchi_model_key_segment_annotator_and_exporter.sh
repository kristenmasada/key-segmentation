
# Definition 2: Tonic and Dominant Chords, Complete Triad
#python3 thresholded_micchi_model_key_segment_annotator_and_exporter.py --threshold 0.98 \
#                                                                       --key_segment_annotator_class 'ThresholdedStrictKeySegmentAnnotator' \
#                                                                       --event_key_probs_npz_path '../frog/out/_2022-05-20_13-45-17/meta-corpus_valid_event_key_probs.npz' \
#                                                                       --ground_truth_key_labels_npz_path '../accuracy_computer/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                                       --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                                       --predicted_rntxt_filepaths_dir '../frog/out/_2022-05-20_13-45-17/'

# Definition 1: Tonic and Dominant Chords
python3 thresholded_micchi_model_key_segment_annotator_and_exporter.py --threshold 0.89 \
                                                                       --key_segment_annotator_class 'ThresholdedBasicKeySegmentAnnotator' \
                                                                       --event_key_probs_npz_path '../frog/out/_2022-05-20_13-45-17/meta-corpus_valid_event_key_probs.npz' \
                                                                       --ground_truth_key_labels_npz_path '../accuracy_computer/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                                                       --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
                                                                       --predicted_rntxt_filepaths_dir '../frog/out/_2022-05-20_13-45-17/'

# Definition 3, Version 2: Tonic and Dominant Harmonies, Allow Root Position VIIo
#python3 thresholded_micchi_model_key_segment_annotator_and_exporter.py --threshold 0.875 \
#                                                                       --key_segment_annotator_class 'ThresholdedRelaxedKeySegmentAnnotator' \
#                                                                       --event_key_probs_npz_path '../frog/out/_2022-05-20_13-45-17/meta-corpus_valid_event_key_probs.npz' \
#                                                                       --ground_truth_key_labels_npz_path '../accuracy_computer/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                                       --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                                       --predicted_rntxt_filepaths_dir '../frog/out/_2022-05-20_13-45-17/'

# Definition 4: Tonic and Dominant Harmonies + All Chromaticism
#python3 thresholded_micchi_model_key_segment_annotator_and_exporter.py --threshold 0.81 \
#                                                                       --key_segment_annotator_class 'ThresholdedChromaticKeySegmentAnnotator' \
#                                                                       --event_key_probs_npz_path '../frog/out/_2022-05-20_13-45-17/meta-corpus_valid_event_key_probs.npz' \
#                                                                       --ground_truth_key_labels_npz_path '../accuracy_computer/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                                       --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                                       --predicted_rntxt_filepaths_dir '../frog/out/_2022-05-20_13-45-17/'