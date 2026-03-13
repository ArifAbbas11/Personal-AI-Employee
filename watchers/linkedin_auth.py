#!/usr/bin/env python3
"""
LinkedIn OAuth Authentication
Run this once to get access token
"""

import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from linkedin_config import (
    LINKEDIN_CLIENT_ID,
    LINKEDIN_CLIENT_SECRET,
    LINKEDIN_AUTHORIZATION_URL,
    LINKEDIN_TOKEN_URL,
    LINKEDIN_REDIRECT_URI,
    LINKEDIN_SCOPES,
    TOKEN_FILE
)

class CallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback"""

    def do_GET(self):
        """Handle GET request with authorization code"""
        print(f"\n📥 Received callback: {self.path}")
        query = urlparse(self.path).query
        params = parse_qs(query)

        print(f"📋 Parameters: {list(params.keys())}")

        if 'code' in params:
            auth_code = params['code'][0]
            print(f"🔑 Authorization code received: {auth_code[:20]}...")
            token_data = self.exchange_code_for_token(auth_code)

            if token_data:
                TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(TOKEN_FILE, 'w') as f:
                    json.dump(token_data, f, indent=2)

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                    <html>
                    <body style="font-family: Arial; padding: 50px; text-align: center;">
                    <h1 style="color: green;">Success!</h1>
                    <p>LinkedIn authentication successful.</p>
                    <p>You can close this window and return to the terminal.</p>
                    </body>
                    </html>
                ''')

                print(f"\n✅ Token saved to: {TOKEN_FILE}")
                print("✅ You can now use LinkedIn auto-posting!")
            else:
                print("❌ Token exchange failed")
                self.send_error(500, "Failed to get access token")
        elif 'error' in params:
            error = params['error'][0]
            error_desc = params.get('error_description', ['Unknown error'])[0]
            print(f"❌ LinkedIn returned error: {error}")
            print(f"❌ Description: {error_desc}")
            self.send_error(400, f"LinkedIn error: {error}")
        else:
            print("❌ No authorization code or error in callback")
            print(f"❌ Received parameters: {params}")
            self.send_error(400, "No authorization code received")

    def exchange_code_for_token(self, auth_code):
        """Exchange authorization code for access token"""
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': LINKEDIN_REDIRECT_URI,
            'client_id': LINKEDIN_CLIENT_ID,
            'client_secret': LINKEDIN_CLIENT_SECRET
        }

        try:
            response = requests.post(LINKEDIN_TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error getting token: {e}")
            return None

    def log_message(self, format, *args):
        """Suppress log messages"""
        pass

def main():
    """Main authentication flow"""
    print("🔐 LinkedIn OAuth Authentication")
    print("=" * 50)
    print()

    if LINKEDIN_CLIENT_ID == 'YOUR_CLIENT_ID_HERE':
        print("❌ Error: LinkedIn credentials not configured")
        print()
        print("Please edit watchers/linkedin_config.py and add:")
        print("  - LINKEDIN_CLIENT_ID")
        print("  - LINKEDIN_CLIENT_SECRET")
        print()
        print("Get these from: https://www.linkedin.com/developers/apps")
        return

    scope_string = '%20'.join(LINKEDIN_SCOPES)
    auth_url = (
        f"{LINKEDIN_AUTHORIZATION_URL}"
        f"?response_type=code"
        f"&client_id={LINKEDIN_CLIENT_ID}"
        f"&redirect_uri={LINKEDIN_REDIRECT_URI}"
        f"&scope={scope_string}"
    )

    print("Step 1: Opening browser for LinkedIn authorization...")
    print()
    print("If browser doesn't open, copy this URL:")
    print(auth_url)
    print()

    webbrowser.open(auth_url)

    print("Step 2: Authorize the app in your browser")
    print("Step 3: You'll be redirected back (wait for success message)")
    print()
    print("Starting local server on http://localhost:8080...")
    print()

    server = HTTPServer(('localhost', 8080), CallbackHandler)
    server.handle_request()

    print()
    print("✅ Authentication complete!")

if __name__ == '__main__':
    main()
