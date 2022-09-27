# Definition 2: Tonic and Dominant Chords, Complete Triad
echo 'Definition 2: Tonic and Dominant Chords, Complete Triad'
python3 clear_key_segment_results_computer.py --event_key_preds_npz_path 'in/meta-corpus_validation_frog_event_key_preds_2022-05-12_17-00-11.npz' \
                                              --pred_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_pred_key_segment_boundaries_def2.npz' \
                                              --ground_truth_event_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                              --ground_truth_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_ground_truth_key_segment_boundaries_def2.npz' \
                                              --table '6.5'

# Definition 1: Tonic and Dominant Chords
echo -e '\nDefinition 1: Tonic and Dominant Chords'
python3 clear_key_segment_results_computer.py --event_key_preds_npz_path 'in/meta-corpus_validation_frog_event_key_preds_2022-05-12_17-00-11.npz' \
                                              --pred_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_pred_key_segment_boundaries_def1.npz' \
                                              --ground_truth_event_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                              --ground_truth_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_ground_truth_key_segment_boundaries_def1.npz' \
                                              --table '6.5'

# Definition 3, Version 1: Tonic and Dominant Harmonies, No Root Position VIIo
echo -e '\nDefinition 3, Version 1: Tonic and Dominant Harmonies, No Root Position VIIo'
python3 clear_key_segment_results_computer.py --event_key_preds_npz_path 'in/meta-corpus_validation_frog_event_key_preds_2022-05-12_17-00-11.npz' \
                                              --pred_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_pred_key_segment_boundaries_def3v1.npz' \
                                              --ground_truth_event_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                              --ground_truth_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_ground_truth_key_segment_boundaries_def3v1.npz' \
                                              --table '6.5'

# Definition 3, Version 2: Tonic and Dominant Harmonies, Allow Root Position VIIo
echo -e '\nDefinition 3, Version 2: Tonic and Dominant Harmonies, Allow Root Position VIIo'
python3 clear_key_segment_results_computer.py --event_key_preds_npz_path 'in/meta-corpus_validation_frog_event_key_preds_2022-05-12_17-00-11.npz' \
                                              --pred_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_pred_key_segment_boundaries_def3v2.npz' \
                                              --ground_truth_event_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                              --ground_truth_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_ground_truth_key_segment_boundaries_def3v2.npz' \
                                              --table '6.5'

# Definition 6: Tonic and Dominant Harmonies + Neapolitan Chords
echo -e '\nDefinition 6: Tonic and Dominant Harmonies + Neapolitan Chords'
python3 clear_key_segment_results_computer.py --event_key_preds_npz_path 'in/meta-corpus_validation_frog_event_key_preds_2022-05-12_17-00-11.npz' \
                                              --pred_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_pred_key_segment_boundaries_def6v2.npz' \
                                              --ground_truth_event_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                              --ground_truth_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_ground_truth_key_segment_boundaries_def6v2.npz' \
                                              --table '6.5'

# Definition 7: Tonic and Dominant Harmonies + Augmented 6th Chords
echo -e '\nDefinition 7: Tonic and Dominant Harmonies + Augmented 6th Chords'
python3 clear_key_segment_results_computer.py --event_key_preds_npz_path 'in/meta-corpus_validation_frog_event_key_preds_2022-05-12_17-00-11.npz' \
                                               --pred_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_pred_key_segment_boundaries_def7v2.npz' \
                                               --ground_truth_event_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                               --ground_truth_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_ground_truth_key_segment_boundaries_def7v2.npz' \
                                               --table '6.5'

# Definition 5: Tonic and Dominant Harmonies + Mixture
echo -e '\nDefinition 5: Tonic and Dominant Harmonies + Mixture'
python3 clear_key_segment_results_computer.py --event_key_preds_npz_path 'in/meta-corpus_validation_frog_event_key_preds_2022-05-12_17-00-11.npz' \
                                              --pred_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_pred_key_segment_boundaries_def5v2.npz' \
                                              --ground_truth_event_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                              --ground_truth_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_ground_truth_key_segment_boundaries_def5v2.npz' \
                                              --table '6.5'

# Definition 4: Tonic and Dominant Harmonies + All Chromaticism
echo -e '\nDefinition 4: Tonic and Dominant Harmonies + All Chromaticism'
python3 clear_key_segment_results_computer.py --event_key_preds_npz_path 'in/meta-corpus_validation_frog_event_key_preds_2022-05-12_17-00-11.npz' \
                                              --pred_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_pred_key_segment_boundaries_def4v2.npz' \
                                              --ground_truth_event_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                              --ground_truth_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_ground_truth_key_segment_boundaries_def4v2.npz' \
                                              --table '6.5'

# Definition 8: All Events, No Tonicization
echo -e '\nDefinition 8: All Events, No Tonicization'
python3 clear_key_segment_results_computer.py --event_key_preds_npz_path 'in/meta-corpus_validation_frog_event_key_preds_2022-05-12_17-00-11.npz' \
                                              --pred_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_pred_key_segment_boundaries_def8.npz' \
                                              --ground_truth_event_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                              --ground_truth_key_segment_boundaries_npz_path 'in/key_segment_boundaries/meta-corpus_validation_ground_truth_key_segment_boundaries_def8.npz' \
                                              --table '6.5'

# Definition 9. All Events
echo -e '\nDefinition 9: All Events'
python3 clear_key_segment_results_computer.py --event_key_preds_npz_path 'in/meta-corpus_validation_frog_event_key_preds_2022-05-12_17-00-11.npz' \
                                              --ground_truth_event_key_labels_npz_path 'in/meta-corpus_validation_ground_truth_event_key_labels.npz' \
                                              --table '6.5'