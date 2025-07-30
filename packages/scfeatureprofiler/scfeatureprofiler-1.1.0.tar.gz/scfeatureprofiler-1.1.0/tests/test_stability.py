# tests/test_stability.py

import pytest
import numpy as np
import pandas as pd

from scfeatureprofiler._stability import _calculate_stability_scores


@pytest.fixture
def stability_test_data():
    """Creates a mock per-condition results DataFrame for testing."""
    data = {
        'feature_id':   ['GeneA', 'GeneA', 'GeneA', 'GeneB', 'GeneB', 'GeneB'],
        'group':        ['T-cell', 'T-cell', 'T-cell', 'B-cell', 'B-cell', 'B-cell'],
        'condition':    ['c1', 'c2', 'c3', 'c1', 'c2', 'c3'],
        'pct_expressing': [80.0, 82.0, 78.0, 90.0, 50.0, 10.0], # GeneA is stable, GeneB is not
        'norm_score':   [0.9, 0.9, 0.9, 0.8, 0.8, 0.8],
        'mean_all':     [5.0, 5.1, 4.9, 6.0, 3.0, 1.0],
        'p_val_marker': [1e-10, 1e-10, 1e-10, 1e-20, 1e-20, 1e-20],
        'fdr_marker':   [1e-9, 1e-9, 1e-9, 1e-19, 1e-19, 1e-19],
        'specificity_tau': [0.95, 0.95, 0.95, 0.98, 0.98, 0.98],
    }
    return pd.DataFrame(data)


def test_multi_condition_stability(stability_test_data):
    """Test that stability score is calculated correctly for multiple conditions."""
    results = _calculate_stability_scores(stability_test_data, 'specificity_tau')
    
    assert 'stability_score' in results.columns
    assert results.shape[0] == 2 # One row per feature/group combo
    
    # Check the stable gene (GeneA)
    gene_a_stats = results[results['feature_id'] == 'GeneA'].iloc[0]
    # CV of [80, 82, 78] is very low (~0.025), so stability should be high (~0.975)
    assert gene_a_stats['stability_score'] > 0.95
    
    # Check the unstable gene (GeneB)
    gene_b_stats = results[results['feature_id'] == 'GeneB'].iloc[0]
    # CV of [90, 50, 10] is high (~0.8), so stability should be low (~0.2)
    assert gene_b_stats['stability_score'] < 0.3


def test_single_condition_stability(stability_test_data):
    """Test that stability is 1.0 when only one condition is present."""
    single_condition_data = stability_test_data[stability_test_data['condition'] == 'c1']
    
    results = _calculate_stability_scores(single_condition_data, 'specificity_tau')
    
    assert 'stability_score' in results.columns
    # All stability scores should be 1.0
    assert (results['stability_score'] == 1.0).all()


def test_no_condition_column(stability_test_data):
    """Test that the function works if the 'condition' column is missing."""
    no_condition_data = stability_test_data.drop(columns=['condition'])
    
    results = _calculate_stability_scores(no_condition_data, 'specificity_tau')
    
    assert 'stability_score' in results.columns
    # Stability should default to 1.0
    assert (results['stability_score'] == 1.0).all()