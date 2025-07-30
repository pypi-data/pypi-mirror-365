import requests
import re
import urllib.parse
import sys

# Internal "private" functions, not meant to be called directly from outside the module.

def _deobfuscate_script(obfuscated_string, key_string, offset, base):
    """
    De-obfuscates the specific type of JavaScript found on the Kwik video service.
    """
    def _decode_base(wu, xe, q):
        chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/+"
        h = chars[:xe]
        i = chars[:q]
        j = 0
        for idx, char_val in enumerate(reversed(wu)):
            if char_val in h:
                j += h.index(char_val) * (xe ** idx)
        if j == 0: return "0"
        k = ""
        while j > 0:
            k = i[j % q] + k
            j //= q
        return k or "0"

    try:
        delimiter = key_string[base]
        parts = obfuscated_string.split(delimiter)
        key_map = {char: str(i) for i, char in enumerate(key_string)}
        result_chars = []
        for s in parts:
            if not s: continue
            for char, index in key_map.items():
                s = s.replace(char, index)
            decoded_val_str = _decode_base(s, base, 10)
            char_code = int(decoded_val_str) - offset
            result_chars.append(chr(char_code))
        final_string = "".join(result_chars)
        return urllib.parse.unquote(final_string)
    except Exception as e:
        print(f"[Module Error] Deobfuscation failed: {e}", file=sys.stderr)
        return ""

def _get_link_from_kwik(kwik_url, session):
    """
    Takes a kwik.si URL and returns the final direct download link.
    """
    try:
        # 1. Fetch Kwik page
        kwik_response = session.get(kwik_url, timeout=15)
        kwik_response.raise_for_status()
        html_content = kwik_response.text

        # 2. Find and decode the script
        pattern = re.compile(r'eval\(function\(.*?\}\("(.+?)",\d+,"(.+?)",(\d+),(\d+),.*?\)\)', re.DOTALL)
        match = pattern.search(html_content)
        if not match:
            print("[Module Error] Could not find obfuscated script on Kwik page.", file=sys.stderr)
            return None

        params = {
            'obfuscated_string': match.group(1),
            'key_string': match.group(2),
            'offset': int(match.group(3)),
            'base': int(match.group(4))
        }
        decoded_script = _deobfuscate_script(**params)
        if not decoded_script:
            return None

        # 3. Extract form data
        form_action_match = re.search(r'action="([^"]+)"', decoded_script)
        token_match = re.search(r'name="_token" value="([^"]+)"', decoded_script)
        if not (form_action_match and token_match):
            print("[Module Error] Could not parse form data from decoded script.", file=sys.stderr)
            return None

        post_url = form_action_match.group(1)
        token = token_match.group(1)

        # 4. Send POST request to get the redirect link
        payload = {'_token': token}
        post_headers = {'referer': kwik_url}
        download_response = session.post(post_url, data=payload, headers=post_headers, allow_redirects=False)

        # 5. Return the direct link from the 'Location' header
        return download_response.headers.get('Location')

    except requests.exceptions.RequestException as e:
        print(f"[Module Error] Request failed during Kwik processing: {e}", file=sys.stderr)
        return None

# --- Public Function ---
def get_direct_link(pahe_url):
    """
    Main public function. Takes a pahe.win URL and returns the direct Kwik download link.

    Args:
        pahe_url (str): The URL from pahe.win (e.g., 'https://pahe.win/WtJtk').

    Returns:
        str: The final direct download link, or None if any step fails.
    """
    # Use a single session object for the entire process
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'okhttp/5.0.0-alpha.14'
    })

    try:
        # 1. Get the pahe.win page
        response = session.get(pahe_url, timeout=10)
        response.raise_for_status()

        # 2. Find the intermediate kwik.si URL
        kwik_url_match = re.search(r'"(https://kwik\.si/f/[^"]+)"', response.text)
        if not kwik_url_match:
            print(f"[Module Error] Could not find a kwik.si link on {pahe_url}", file=sys.stderr)
            return None
        
        kwik_url = kwik_url_match.group(1)
        
        # 3. Process the Kwik URL to get the final link
        return _get_link_from_kwik(kwik_url, session)

    except requests.exceptions.RequestException as e:
        print(f"[Module Error] Failed to fetch the pahe.win URL: {e}", file=sys.stderr)
        return None

# This block allows the script to be run directly from the command line for testing
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"This script is a module. To use it, import it in another script.")
        print(f"Example: from generator import get_direct_link")
        print(f"\nFor testing, you can run it directly with a URL:")
        print(f"Usage: python {sys.argv[0]} <pahe.win_url>")
        sys.exit(1)
        
    test_url = sys.argv[1]
    print(f"--- Testing generator module with URL: {test_url} ---")
    
    direct_link = get_direct_link(test_url)
    
    if direct_link:
        print(f"\n[SUCCESS] Direct Link Found:")
        print(direct_link)
    else:
        print("\n[FAILED] Could not retrieve the direct link.")
