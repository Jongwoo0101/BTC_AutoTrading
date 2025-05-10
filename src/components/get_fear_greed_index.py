import requests
import datetime

fear_greed_api = "https://api.alternative.me/fng/"

def get_fear_greed_index(limit=7):
        """공포탐욕지수 데이터 조회"""
        try:
            response = requests.get(f"{fear_greed_api}?limit={limit}")
            if response.status_code == 200:
                data = response.json()
               
                latest = data['data'][0]
                print("\n=== Fear and Greed Index ===")
                print(f"Current Value: {latest['value']} ({latest['value_classification']})")
               
                processed_data = []
                for item in data['data']:
                    processed_data.append({
                        'date': datetime.fromtimestamp(int(item['timestamp'])).strftime('%Y-%m-%d'),
                        'value': int(item['value']),
                        'classification': item['value_classification']
                    })
               
                values = [int(item['value']) for item in data['data']]
                avg_value = sum(values) / len(values)
                trend = 'Improving' if values[0] > avg_value else 'Deteriorating'
               
                return {
                    'current': {
                        'value': int(latest['value']),
                        'classification': latest['value_classification']
                    },
                    'history': processed_data,
                    'trend': trend,
                    'average': avg_value
                }
               
            return None
        except Exception as e:
            print(f"Error in get_fear_greed_index: {e}")
            return None