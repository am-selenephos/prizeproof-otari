import json,threading,unittest
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from app import build_server
class WebsiteTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=build_server('127.0.0.1',0)
  cls.port=cls.s.server_address[1]
  cls.t=threading.Thread(target=cls.s.serve_forever,daemon=True);cls.t.start()
 @classmethod
 def tearDownClass(cls):cls.s.shutdown();cls.s.server_close();cls.t.join(timeout=3)
 def get(self,path):
  with urlopen(f'http://127.0.0.1:{self.port}{path}',timeout=5) as r:return r.status,r.read().decode(),dict(r.headers)
 def test_home_and_assets(self):
  status,body,h=self.get('/')
  self.assertEqual(status,200);self.assertIn('PrizeProof',body);self.assertIn('Content-Security-Policy',h)
  for f in ['app.css','app.js']:
   code,content,_=self.get('/'+f);self.assertEqual(code,200);self.assertTrue(len(content)>100)
 def test_health_no_key_leak(self):
  status,b,h=self.get('/api/health')
  d=json.loads(b);self.assertEqual(status,200);self.assertIn('otari_configured',d);self.assertNotIn('api_key',b.lower())
 def test_demo_no_paid_claim(self):
  status,b,h=self.get('/api/demo')
  d=json.loads(b);self.assertEqual(status,200);self.assertFalse(d['payment_verified']);self.assertFalse(d['submission_completed']);self.assertTrue(d['demo'])
 def test_rejects_unapproved_url(self):
  req=Request(f'http://127.0.0.1:{self.port}/api/evaluate',data=json.dumps({'url':'http://127.0.0.1:1234/admin'}).encode(),headers={'Content-Type':'application/json'},method='POST')
  with self.assertRaises(HTTPError) as ctx:urlopen(req,timeout=5)
  self.assertEqual(ctx.exception.code,400)
  ctx.exception.close()
 def test_local_model_opt_in_required(self):
  req=Request(f'http://127.0.0.1:{self.port}/api/evaluate',data=json.dumps({'url':'https://github.com/Expensify/App/issues/105145','use_local_ai':True}).encode(),headers={'Content-Type':'application/json'},method='POST')
  with self.assertRaises(HTTPError) as ctx:urlopen(req,timeout=5)
  self.assertEqual(ctx.exception.code,409)
  ctx.exception.close()
 def test_unknown_route_is_404(self):
  with self.assertRaises(HTTPError) as ctx:self.get('/server.env')
  self.assertEqual(ctx.exception.code,404)
  ctx.exception.close()
if __name__=='__main__':unittest.main()
