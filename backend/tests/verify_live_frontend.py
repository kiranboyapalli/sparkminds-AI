import urllib.request
import re

def verify_live_frontend():
    print("Testing live Railway frontend bundle...")
    url = "https://sparkminds-ai.up.railway.app"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req).read().decode("utf-8")
    print(f"1. HTML loaded: {len(html)} bytes")
    
    js_match = re.search(r'src="(/assets/index-[^"]+\.js)"', html)
    assert js_match, "JS bundle tag must be present in index.html"
    js_path = js_match.group(1)
    print(f"2. Live JS asset path: {js_path}")
    
    js_req = urllib.request.Request(url + js_path, headers={"User-Agent": "Mozilla/5.0"})
    js_content = urllib.request.urlopen(js_req).read().decode("utf-8")
    print(f"3. Live JS bundle loaded: {len(js_content)} bytes")
    
    # Assert clean registration & sign in requirements
    assert "Already have an account? Sign in" in js_content, "Must have link to sign in for existing users"
    assert "New user? Register" in js_content, "Must have link to register in sign in form"
    assert "Student Full Name" in js_content, "Must have clean Student Full Name title"
    assert "Password or PIN" in js_content, "Must have mandatory Password or PIN"
    
    # Verify service worker cache version
    sw_req = urllib.request.Request(url + "/sw.js", headers={"User-Agent": "Mozilla/5.0"})
    sw_content = urllib.request.urlopen(sw_req).read().decode("utf-8")
    assert "sparkminds-ai-shell-v12" in sw_content, "Must have latest sw cache v12"
    print("4. Service Worker Cache Version: sparkminds-ai-shell-v12 verified!")
    
    print("\n🎉 ALL LIVE FRONTEND REQUIREMENTS CONFIRMED ON https://sparkminds-ai.up.railway.app!")

if __name__ == "__main__":
    verify_live_frontend()
