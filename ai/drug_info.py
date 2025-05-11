import requests

class DrugInfoLookup:
    """Fetch drug information using the OpenFDA API."""
    OPENFDA_ENDPOINT = 'https://api.fda.gov/drug/label.json'

    def search(self, drug_name):
        """Search for a drug by name and return basic info."""
        params = {'search': f'openfda.brand_name:"{drug_name}"', 'limit': 1}
        try:
            response = requests.get(self.OPENFDA_ENDPOINT, params=params)
            response.raise_for_status()
            results = response.json().get('results', [])
            if results:
                info = results[0]
                return {
                    'brand_name': info.get('openfda', {}).get('brand_name', ['N/A'])[0],
                    'generic_name': info.get('openfda', {}).get('generic_name', ['N/A'])[0],
                    'purpose': info.get('purpose', ['N/A'])[0],
                    'indications_and_usage': info.get('indications_and_usage', ['N/A'])[0]
                }
            else:
                return {'error': 'No information found for this drug.'}
        except Exception as e:
            return {'error': str(e)} 