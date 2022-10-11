# GROUND TRUTH KEY SEGMENTS

# Definition 2: Tonic and Dominant Chords, Complete Triad
# NOTE: this takes a while to run.
#python3 ground_truth_key_segment_annotator_and_exporter.py --key_segment_annotator_class 'StrictKeySegmentAnnotator' \
#                                                           --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                           --ground_truth_key_labels_npz_path '../results_computation/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                           --key_segments_output_method "output_key_segment_indices"

# Definition 1: Tonic and Dominant Chords
python3 ground_truth_key_segment_annotator_and_exporter.py --key_segment_annotator_class 'BasicKeySegmentAnnotator' \
                                                           --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
                                                           --ground_truth_key_labels_npz_path '../results_computation/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                                           --key_segments_output_method "output_key_segment_indices"

# Definition 3, Version 1: Tonic and Dominant Harmonies, No Root Position VIIo
#python3 ground_truth_key_segment_annotator_and_exporter.py --key_segment_annotator_class 'RelaxedKeySegmentAnnotator' \
#                                                           --allow_root_position_viio_chords \
#                                                           --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                           --ground_truth_key_labels_npz_path '../results_computation/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                           --key_segments_output_method "output_key_segment_indices"

# Definition 3, Version 2: Tonic and Dominant Harmonies, Allow Root Position VIIo
#python3 ground_truth_key_segment_annotator_and_exporter.py --key_segment_annotator_class 'RelaxedKeySegmentAnnotator' \
#                                                           --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                           --ground_truth_key_labels_npz_path '../results_computation/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                           --key_segments_output_method "output_key_segment_indices"

# Definition 4: Tonic and Dominant Harmonies + All Chromaticism
#python3 ground_truth_key_segment_annotator_and_exporter.py --key_segment_annotator_class 'ChromaticKeySegmentAnnotator' \
#                                                           --allow_root_position_viio_chords \
#                                                           --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                           --ground_truth_key_labels_npz_path '../results_computation/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                           --key_segments_output_method "output_key_segment_indices"

# Definition 5: Tonic and Dominant Harmonies + Mixture
#python3 ground_truth_key_segment_annotator_and_exporter.py --key_segment_annotator_class 'MixtureKeySegmentAnnotator' \
#                                                           --allow_root_position_viio_chords \
#                                                           --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                           --ground_truth_key_labels_npz_path '../results_computation/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                           --key_segments_output_method "output_key_segment_indices"

# Definition 6: Tonic and Dominant Harmonies + Neapolitan Chords
#python3 ground_truth_key_segment_annotator_and_exporter.py --key_segment_annotator_class 'NeapolitanChordsKeySegmentAnnotator' \
#                                                           --allow_root_position_viio_chords \
#                                                           --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                           --ground_truth_key_labels_npz_path '../results_computation/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                           --key_segments_output_method "output_key_segment_indices"

# Definition 7: Tonic and Dominant Harmonies + Augmented 6th Chords
#python3 ground_truth_key_segment_annotator_and_exporter.py --key_segment_annotator_class 'Augmented6thKeySegmentAnnotator' \
#                                                           --allow_root_position_viio_chords \
#                                                           --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                           --ground_truth_key_labels_npz_path '../results_computation/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                           --key_segments_output_method "output_key_segment_indices"

# Definition 8: All Events, No Tonicization
#python3 ground_truth_key_segment_annotator_and_exporter.py --key_segment_annotator_class 'TonicizationKeySegmentAnnotator' \
#                                                           --txt_file_with_mxl_filepaths 'in/meta-corpus_valid_mxl_filepaths.txt' \
#                                                           --ground_truth_key_labels_npz_path '../results_computation/in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                           --key_segments_output_method "output_key_segment_indices"