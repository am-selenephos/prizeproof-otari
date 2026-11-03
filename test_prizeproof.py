import json, tempfile, unittest
from pathlib import Path
from unittest.mock import Mock
import prizeproof as p

class PrizeProofTests(unittest.TestCase):
 def setUp(self):
  self.issue={'html_url':'https://github.com/realco/realrepo/issues/12','title':'Fix API duplicate detection - $250 bounty','state':'open','body':'Fix duplicate creation in API. $250 paid after accepted PR. Requires reproduction tests.','assignee':None,'pull_request':None,'labels':[{'name':'bounty'}]}
 def test_accepts_only_github_issue_url(self):
  self.assertEqual(p.parse_issue_url('https://github.com/realco/realrepo/issues/12'),('realco','realrepo',12))
  for url in ('https://github.com.evil.org/realco/realrepo/issues/12','http://127.0.0.1:8000/a','https://github.com/realco/realrepo/pulls/12','https://github.com/realco/realrepo/issues/12/extra'):
   with self.assertRaises(ValueError):p.parse_issue_url(url)
 def test_closed_issue_is_killed(self):
  i=dict(self.issue,state='closed')
  self.assertEqual(p.score_issue(i)['decision'],'KILL')
 def test_open_unverified_payout_is_hold(self):
  i=dict(self.issue,title='Help Wanted: docs',body='Fix documentation. Payment guaranteed $100000 in crypto send deposit first')
  result=p.score_issue(i)
  self.assertEqual(result['decision'],'KILL')
 def test_unassigned_paid_issue_needs_verification(self):
  d=p.score_issue(self.issue)
  self.assertEqual(d['decision'],'RESEARCH')
  self.assertEqual(d['advertised_amount_usd'],250)
  self.assertFalse(d['payment_verified'])
 def test_extremely_contested_bounty_is_hold(self):
  i=dict(self.issue,comments=500)
  self.assertEqual(p.score_issue(i)['decision'],'HOLD')

 def test_assigned_issue_is_hold(self):
  i=dict(self.issue,assignee={'login':'maintainer'})
  self.assertEqual(p.score_issue(i)['decision'],'HOLD')
 def test_llm_cannot_upgrade_to_paid(self):
  d=p.score_issue(self.issue)
  raw=json.dumps({'summary':'Candidate for local reproduction','decision':'SUBMIT','payment_verified':True,'score':100})
  result=p.attach_model_analysis(d,raw)
  self.assertEqual(result['decision'],'RESEARCH')
  self.assertFalse(result['payment_verified'])
 def test_rejects_unstructured_model_response(self):
  with self.assertRaises(ValueError):p.attach_model_analysis(p.score_issue(self.issue),'NOT_JSON')
 def test_official_otari_hosted_path(self):
  self.assertEqual(p.OTARI_HOSTED,'https://api.otari.ai/api/v1/chat/completions')

 def test_otari_requires_key_and_correct_host(self):
  with self.assertRaises(ValueError):p.ask_otari('hello',api_key='',endpoint='https://api.otari.ai/v1/chat/completions')
  with self.assertRaises(ValueError):p.ask_otari('hello',api_key='test',endpoint='https://hostile.example/v1/chat/completions')
 def test_save_report_is_private(self):
  with tempfile.TemporaryDirectory() as t:
   out=p.save_report(p.score_issue(self.issue),Path(t)/'report.json')
   self.assertEqual(out.stat().st_mode&0o777,0o600)
   self.assertEqual(json.loads(out.read_text())['decision'],'RESEARCH')

if __name__=='__main__':unittest.main()
