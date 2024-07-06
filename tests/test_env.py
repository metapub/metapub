import os

def get_ncbi_api_key():
    ncbi_api_key = os.getenv('NCBI_API_KEY')
    if not ncbi_api_key:
        raise ValueError("NCBI_API_KEY is not set in the environment variables")
    return ncbi_api_key

def test_ncbi_api_key():
    assert get_ncbi_api_key() is not None

