import requests
import json
from typing import Dict, Optional, List
from .auth.login import AxiomAuth

class AxiomTradeClient:
    """
    Main client for interacting with Axiom Trade API
    """
    
    def __init__(self):
        self.auth = AxiomAuth()
        self.access_token = None
        self.refresh_token = None
        self.client_credentials = None
        
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Origin': 'https://axiom.trade',
            'Connection': 'keep-alive',
            'Referer': 'https://axiom.trade/',
            'TE': 'trailers'
        }
    
    def login(self, email: str, b64_password: str, otp_code: str) -> Dict:
        """
        Complete login process and store credentials
        Returns a dictionary containing access_token, refresh_token, and other credentials
        """
        login_result = self.auth.complete_login(email, b64_password, otp_code)
        
        # Extract tokens from the login response
        # The API typically returns tokens in cookies or response body
        if isinstance(login_result, dict):
            # Store the full credentials
            self.client_credentials = login_result
            
            # Extract tokens if available in the response
            self.access_token = login_result.get('accessToken') or login_result.get('access_token')
            self.refresh_token = login_result.get('refreshToken') or login_result.get('refresh_token')
            
            # Return tokens in a standardized format
            return {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'client_credentials': login_result
            }
        
        return login_result
    
    def set_tokens(self, access_token: str = None, refresh_token: str = None):
        """
        Set access and refresh tokens manually
        """
        if access_token:
            self.access_token = access_token
        if refresh_token:
            self.refresh_token = refresh_token
    
    def get_tokens(self) -> Dict[str, Optional[str]]:
        """
        Get current tokens
        """
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        }
    
    def is_authenticated(self) -> bool:
        """
        Check if the client has valid authentication tokens
        """
        return self.access_token is not None
    
    def refresh_access_token(self) -> str:
        """
        Refresh the access token using stored refresh token
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        self.access_token = self.auth.refresh_access_token(self.refresh_token)
        return self.access_token
    
    def get_trending_tokens(self, time_period: str = '1h') -> Dict:
        """
        Get trending meme tokens
        Available time periods: 1h, 24h, 7d
        """
        if not self.access_token:
            raise ValueError("Access token required. Please login or set tokens first.")
        
        url = f'https://api6.axiom.trade/meme-trending?timePeriod={time_period}'
        headers = {
            **self.base_headers,
            'Cookie': f'auth-access-token={self.access_token}'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_token_info(self, token_address: str) -> Dict:
        """
        Get information about a specific token
        """
        if not self.access_token:
            raise ValueError("Access token required. Please login or set tokens first.")
        
        # This endpoint might need to be confirmed with actual API documentation
        url = f'https://api6.axiom.trade/token/{token_address}'
        headers = {
            **self.base_headers,
            'Cookie': f'auth-access-token={self.access_token}'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_portfolio(self) -> Dict:
        """
        Get user's portfolio information
        """
        if not self.access_token:
            raise ValueError("Access token required. Please login or set tokens first.")
        
        # This endpoint might need to be confirmed with actual API documentation
        url = 'https://api6.axiom.trade/portfolio'
        headers = {
            **self.base_headers,
            'Cookie': f'auth-access-token={self.access_token}'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()

# Convenience functions for quick usage
def quick_login_and_get_trending(email: str, b64_password: str, otp_code: str, time_period: str = '1h') -> Dict:
    """
    Quick function to login and get trending tokens in one call
    """
    client = AxiomTradeClient()
    client.login(email, b64_password, otp_code)
    return client.get_trending_tokens(time_period)

def get_trending_with_token(access_token: str, time_period: str = '1h') -> Dict:
    """
    Quick function to get trending tokens with existing access token
    """
    client = AxiomTradeClient()
    client.set_tokens(access_token=access_token)
    return client.get_trending_tokens(time_period)
