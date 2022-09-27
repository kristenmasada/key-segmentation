# Definition 1: Tonic and Dominant Chords
#nice python3 whole_key_segment_stats_plotter.py --event_key_probs_npz_path 'in/meta-corpus_validation_frog_event_key_probs_2022-06-08_11-29-18.npz' \
#                                                --ground_truth_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                --clear_key_definition 'def1' --threshold 0.89 --plot_precision --plot_event_level_recall

# Definition 3, Version 2: Tonic and Dominant Harmonies, Allow Root Position VIIo
#nice python3 whole_key_segment_stats_plotter.py --event_key_probs_npz_path 'in/meta-corpus_validation_frog_event_key_probs_2022-06-08_11-29-18.npz' \
#                                                --ground_truth_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                --clear_key_definition 'def3v2' --threshold 0.875 --plot_precision --plot_event_level_recall

# Definition 4: Tonic and Dominant Harmonies + All Chromaticism
#nice python3 whole_key_segment_stats_plotter.py --event_key_probs_npz_path 'in/meta-corpus_validation_frog_event_key_probs_2022-06-08_11-29-18.npz' \
#                                                --ground_truth_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
#                                                --clear_key_definition 'def4v2' --threshold 0.81 --plot_precision --plot_event_level_recall