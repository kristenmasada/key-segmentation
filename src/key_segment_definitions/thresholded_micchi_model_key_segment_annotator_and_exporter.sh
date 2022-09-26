
# 1. Strict key segments
#python3 thresholded_micchi_model_key_segment_annotator_and_exporter.py --threshold 0.98 \
#                                                                       --key_segment_annotator_class 'ThresholdedStrictKeySegmentAnnotator' \
#                                                                       --event_key_probs_npz_path '../frog/out/_2022-05-20_13-45-17/meta-corpus_valid_event_key_probs.npz' \
#                                                                       --ground_truth_key_labels_npz_path '../accuracy_computer/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                                       --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                                       --predicted_rntxt_filepaths_dir '../frog/out/_2022-05-20_13-45-17/'

# 2. Basic key segments
python3 thresholded_micchi_model_key_segment_annotator_and_exporter.py --threshold 0.89 \
                                                                       --key_segment_annotator_class 'ThresholdedBasicKeySegmentAnnotator' \
                                                                       --event_key_probs_npz_path '../frog/out/_2022-05-20_13-45-17/meta-corpus_valid_event_key_probs.npz' \
                                                                       --ground_truth_key_labels_npz_path '../accuracy_computer/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                                                       --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
                                                                       --predicted_rntxt_filepaths_dir '../frog/out/_2022-05-20_13-45-17/'

# 4. Relaxed key segments (allow root position viio chords)
#python3 thresholded_micchi_model_key_segment_annotator_and_exporter.py --threshold 0.875 \
#                                                                       --key_segment_annotator_class 'ThresholdedRelaxedKeySegmentAnnotator' \
#                                                                       --event_key_probs_npz_path '../frog/out/_2022-05-20_13-45-17/meta-corpus_valid_event_key_probs.npz' \
#                                                                       --ground_truth_key_labels_npz_path '../accuracy_computer/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                                       --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                                       --predicted_rntxt_filepaths_dir '../frog/out/_2022-05-20_13-45-17/'

# 8. Chromatic key segments
#python3 thresholded_micchi_model_key_segment_annotator_and_exporter.py --threshold 0.81 \
#                                                                       --key_segment_annotator_class 'ThresholdedChromaticKeySegmentAnnotator' \
#                                                                       --event_key_probs_npz_path '../frog/out/_2022-05-20_13-45-17/meta-corpus_valid_event_key_probs.npz' \
#                                                                       --ground_truth_key_labels_npz_path '../accuracy_computer/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                                       --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                                       --predicted_rntxt_filepaths_dir '../frog/out/_2022-05-20_13-45-17/'