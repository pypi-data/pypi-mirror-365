from unittest.mock import patch
from pokeops.pipeline import run_pipeline

def test_run_pipeline(monkeypatch):
    # Mock variable d'environnement
    monkeypatch.setenv("PROCESSED_DIR", "/fake/processed")
    monkeypatch.delenv("RAW_DIR", raising=False)
    
    with patch('pokeops.pipeline.get_raw_dir', return_value='/fake/raw') as mock_get_raw_dir, \
         patch('pokeops.pipeline.ingest', return_value=('/fake/raw/file.json', 5)) as mock_ingest, \
         patch('pokeops.pipeline.get_latest_data', return_value='/fake/raw/file.json') as mock_get_latest_data, \
         patch('pokeops.pipeline.read_raw_json', return_value=[{'name': 'pikachu'}]) as mock_read_raw_json, \
         patch('pokeops.pipeline.extraire_et_sauvegarder_tout') as mock_extraire_et_sauvegarder_tout:

        run_pipeline(skip_ingest=False)

        mock_get_raw_dir.assert_called()
        mock_ingest.assert_called_once()
        mock_get_latest_data.assert_called_once()
        mock_read_raw_json.assert_called_once_with('/fake/raw/file.json')
        mock_extraire_et_sauvegarder_tout.assert_called_once()
