def test_imports():
    import plotverse as pv
    assert hasattr(pv, 'DataFrame')
    assert hasattr(pv, 'plt_plot')
    assert hasattr(pv, 'sns_heatmap')
