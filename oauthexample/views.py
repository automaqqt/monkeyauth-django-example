from django.shortcuts import render,redirect
import secrets,string, requests,json, time,datetime
from requests_oauthlib import OAuth2Session
import os

## insecure setting for localhost demo ##
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

## Client secrets ##
client_id = "9TqfQBiXPrA6tX7T3Bpw5oDD1je191MW8gN6b01p"
client_secret = "DKEjNQDdNvhOGa08pRMZlupk5Nj71H5LcIa32b2983uSe9cPiJSMf85kK18sQSJPj5nbHceOzr88ovvUaj9mKXI4brJgGfLPv0tNig3Eoo32cJw7VJnEjZzmmpbw5tWh"

## URLs ##
token_url = 'http://cmdev.cmstats.net/o/token/'
callback_uri = "http://127.0.0.1:8000/noexit/callback"
auth_url = 'http://cmdev.cmstats.net/o/authorize'


def index(request):
    """Create URI base for authorization.
    """
    nonce = ''.join((secrets.choice(string.ascii_letters) for i in range(10)))    
    url = f"{auth_url}?response_type=code&state={nonce}&client_id={client_id}"

    context= {
			"authurl":url
    }
    return render(request, 'index.html',context)

def callback(request):
    """Callback with token fetch.
    """
    sess = OAuth2Session(client_id, redirect_uri=callback_uri,
                           state=request.GET.get('state'))
    token = sess.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.get_full_path())
    request.session['oauth_token'] = token    
    return redirect('/profile')


def profile(request):
    """Profile view with example for restricted query on full user info.
    """
    sess = OAuth2Session(client_id, token=request.session['oauth_token'])
    resp = sess.get('http://cmdev.cmstats.net/accounts/api/v1/fulluser/').json()
    token = request.session['oauth_token']

    user = resp["user"]
    BAN = resp["ban"]
    eth = resp["ethaddress"]
    discord = resp["discord"]    
    expires = datetime.datetime.fromtimestamp(token['expires_at'])
    tokenview = token['access_token']
    refresh = token['refresh_token']

    context= {
			"request":request, "user":user,"ban":BAN,"eth":eth,"disc":discord,
            'token':tokenview,'refresh':refresh,'expires':expires
    }
    return render(request, 'profile.html',context)

def manual_refresh(request):
    """Refreshing an OAuth 2 token using a refresh token.
    """
    token = request.session['oauth_token']

    extra = {
        'client_id': client_id,
        'client_secret': client_secret,
    }

    sess = OAuth2Session(client_id, token=token)
    request.session['oauth_token'] = sess.refresh_token(token_url, **extra)
    return redirect('/profile')

def auto_login(request):
    """Check for token and refresh or redirect to auth.
    """
    if "oauth_token" in request.session.keys():
        return manual_refresh(request)
    else:
        nonce = ''.join((secrets.choice(string.ascii_letters) for i in range(10)))
        return redirect(f"{auth_url}?response_type=code&state={nonce}&client_id={client_id}&scope=full")