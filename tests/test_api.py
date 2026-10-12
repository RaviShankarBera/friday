import unittest,os,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
from fastapi.testclient import TestClient
import app
class TestAPI(unittest.TestCase):
 def setUp(self):self.client=TestClient(app.app)
 def test_health(self):
  data=self.client.get('/api/health').json();self.assertFalse(data['deviceAccess']);self.assertFalse(data['webAccess'])
 def test_auth_gate(self):self.assertEqual(self.client.get('/api/tasks').status_code,401)
 def test_invalid_token(self):
  os.environ['FIREBASE_PROJECT_ID']='test';self.assertEqual(self.client.get('/api/tasks',headers={'Authorization':'Bearer nonsense'}).status_code,401)
 def test_no_secret_in_config(self):
  os.environ['GEMINI_API_KEY']='secret_value';self.assertNotIn('secret_value',self.client.get('/api/config').text)
 def test_owner_escape(self):self.assertEqual(app.owner('a&user_id=eq.b'),'user_id=eq.a%26user_id%3Deq.b')
 def test_local_truth(self):
  import asyncio
  os.environ['AI_PROVIDER']='local';r=asyncio.run(app.agent('send email',[],'u'));self.assertIn('no external action',r['text'])
if __name__=='__main__':unittest.main()
