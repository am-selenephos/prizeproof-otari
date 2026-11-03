#!/usr/bin/env python3
"""PrizeProof browser surface, local by default, no application credentials or outgoing actions."""
import json
import os
import sys
import time
from collections import defaultdict,deque
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from urllib.error import HTTPError as URLHTTPError

import prizeproof as core

ROOT=Path(__file__).resolve().parent
RATE=defaultdict(deque)
MAX_BODY=900
MAX_RPS_WINDOW=60
MAX_REQUESTS=12

class Handler(BaseHTTPRequestHandler):
 def log_message(self,fmt,*args):
  # Never log user-provided issue URLs.
  return
 def send(self,code,data,typ='application/json; charset=utf-8'):
  if isinstance(data,str):body=data.encode()
  elif isinstance(data,bytes):body=data
  else:body=json.dumps(data,ensure_ascii=True).encode()
  self.send_response(code)
  self.send_header('Content-Type',typ)
  self.send_header('Content-Length',str(len(body)))
  self.send_header('X-Content-Type-Options','nosniff')
  self.send_header('Cache-Control','no-store')
  self.send_header('Referrer-Policy','no-referrer')
  self.send_header('X-Frame-Options','DENY')
  self.send_header('Content-Security-Policy', "default-src 'self'; connect-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
  self.end_headers()
  self.wfile.write(body)
 def do_GET(self):
  route=urlsplit(self.path).path
  if route=='/':
   return self.send(200,(ROOT/'index.html').read_bytes(),'text/html; charset=utf-8')
  if route=='/app.css':
   return self.send(200,(ROOT/'app.css').read_bytes(),'text/css; charset=utf-8')
  if route=='/app.js':
   return self.send(200,(ROOT/'app.js').read_bytes(),'application/javascript; charset=utf-8')
  if route=='/api/health':
   return self.send(200,{'ok':True,'project':'PrizeProof','version':'0.1.0','otari_configured':bool(os.getenv('OTARI_AI_TOKEN')),'issue_source':'GitHub API','submissions_enabled':False})
  if route=='/api/demo':
   return self.send(200,{**core.score_issue(core.DEMO_ISSUE),'demo':True})
  return self.send(404,{'error':'Not found'})
 def do_POST(self):
  if self.path!='/api/evaluate':return self.send(404,{'error':'Not found'})
  now=time.monotonic()
  r=RATE[self.client_address[0]]
  while r and r[0]<now-MAX_RPS_WINDOW:r.popleft()
  if len(r)>=MAX_REQUESTS:return self.send(429,{'error':'Rate limit reached. Try later.'})
  r.append(now)
  try:
   n=int(self.headers.get('Content-Length','0'))
   if not 2<=n<=MAX_BODY:return self.send(413,{'error':'Invalid payload length'})
   obj=json.loads(self.rfile.read(n))
   if not isinstance(obj,dict) or not isinstance(obj.get('url'),str):raise ValueError('GitHub issue URL is required')
   core.parse_issue_url(obj['url'])
   if obj.get('use_otari') and not os.getenv('OTARI_AI_TOKEN'):
    return self.send(409,{'error':'Otari hosted token not configured. Add it to the server environment, never the browser.'})
   issue=core.fetch_issue(obj['url'])
   result=core.score_issue(issue)
   if obj.get('use_otari'):
    review=core.ask_otari(json.dumps({'issue_title':issue.get('title'),'untrusted_issue_description':str(issue.get('body',''))[:8000],'deterministic_review':result},ensure_ascii=True))
    result=core.attach_model_analysis(result,review)
   return self.send(200,result)
  except (ValueError,TypeError,json.JSONDecodeError) as e:
   return self.send(400,{'error':str(e)[:150]})
  except (TimeoutError,ConnectionError,URLHTTPError,KeyError) as e:
   return self.send(502,{'error':'Upstream request failed or returned unexpected structure'})
  except Exception:
   return self.send(502,{'error':'Upstream unavailable. No payment claims were made.'})

def build_server(host='127.0.0.1',port=4417):
 return ThreadingHTTPServer((host,port),Handler)

if __name__=='__main__':
 host=os.getenv('PRIZEPROOF_HOST','127.0.0.1')
 port=int(os.getenv('PRIZEPROOF_PORT','4417'))
 if host!='127.0.0.1':raise SystemExit('PrizeProof preview binds only to loopback. Put it behind approved auth for external access.')
 s=build_server(host,port)
 print('PrizeProof local preview listening',host,port,flush=True)
 try:s.serve_forever()
 except KeyboardInterrupt:pass
 finally:s.server_close()
