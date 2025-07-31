def test_version():
    import daedaluspy
    assert hasattr(daedaluspy, '__version__') or hasattr(daedaluspy, 'version')
