def test_import_daedaluspy():
    try:
        import daedaluspy
    except ImportError:
        import pytest
        pytest.fail('Não foi possível importar o pacote daedaluspy')
