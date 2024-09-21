from rest_framework.views import APIView
from rest_framework.response import Response
from decouple import config
import requests
import json


def auth_fedex():
    try:
        # Input Data
        data = {
            'grant_type': 'client_credentials',
            'client_id': config('FEDEX_API_KEY'),
            'client_secret': config('FEDEX_SECRET_KEY')
        }
        # Headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Make API Call
        response = response = requests.post(
            f"{config('FEDEX_BASE_API_URL')}/oauth/token", data=data, headers=headers)

        return response.json()
    except Exception as e:
        print('Error authenticating with FedEx API:', e)
        raise ValueError('Failed to authenticate with FedEx API')


class FedexTrackingView(APIView):
    def post(self, req):
        authRes = auth_fedex()
        tracking_number = req.data.get('trackingNumber')
        # Input Data
        data = json.dumps({
            'includeDetailedScans': True,
            'trackingInfo': [
                {
                    'trackingNumberInfo': {
                        'trackingNumber': tracking_number
                    }
                }
            ]
        })
        headers = {
            'Content-Type': "application/json",
            'X-locale': "en_US",
            'Authorization': "Bearer "+authRes["access_token"]
        }

        # Make API Call
        response = requests.post(
            f"{config('FEDEX_BASE_API_URL')}/track/v1/trackingnumbers", data=data, headers=headers)

        if response.status_code == 200:
            data = response.json()[
                "output"]["completeTrackResults"][0]["trackResults"][0]["scanEvents"]
            # Extract eventdescriptions and cities using list comprehensions
            tracking_details = [{'eventDescription': event.get('eventDescription', ''), 'city': event.get(
                'scanLocation', {}).get('city', '')} for event in data]
            return Response({"tracking_details": tracking_details})
        else:
            return Response({'error': 'Failed to fetch tracking information'}, status=response.status_code)
