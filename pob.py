''' writes a PoB XML to stdout '''

import base64
import sys
import zlib

import httpx

def main():
	res = httpx.get('https://poe.ninja/pob/raw/' + sys.argv[1])
	res.raise_for_status()
	pob_xml = zlib.decompress(base64.urlsafe_b64decode(res.text)).decode('utf-8')
	print(pob_xml)

if __name__ == '__main__':
	main()
