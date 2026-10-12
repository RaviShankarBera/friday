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

class TestAuthenticatedFlows(unittest.TestCase):
 def setUp(self):
  self.client=TestClient(app.app)
  async def owner():return {'sub':'user_a','email':'rsbera707@gmail.com','email_verified':True}
  app.app.dependency_overrides[app.identity]=owner
  self.orig=app.database;self.calls=[]
  async def fake_db(table,method='GET',query='',body=None):
   self.calls.append((table,method,query,body))
   if table=='rpc/fail_stale_tasks':return None
   if table=='tasks' and method=='GET':return []
   if table=='messages' and method=='GET':return []
   return [body] if body else []
  app.database=fake_db;os.environ['AI_PROVIDER']='local'
 def tearDown(self):app.database=self.orig;app.app.dependency_overrides.clear()
 def test_task_lifecycle_and_owner(self):
  r=self.client.post('/api/tasks',json={'prompt':'send email'})
  self.assertEqual(r.status_code,200);self.assertEqual(r.json()['mode'],'local');self.assertIn('no external action',r.json()['result'])
  states=[c[3]['status'] for c in self.calls if c[0]=='tasks' and c[1] in ['POST','PATCH']]
  self.assertEqual(states,['queued','running','done'])
  for c in self.calls:
   if c[0] in ['tasks','messages'] and c[1] in ['GET','PATCH']:self.assertIn('user_id=eq.user_a',c[2])
 def test_memory_delete_scoped(self):
  self.assertEqual(self.client.delete('/api/memory').status_code,200)
  self.assertEqual(self.calls[0][:3],('messages','DELETE','?user_id=eq.user_a'))
 def test_resend_stays_off(self):self.assertEqual(self.client.post('/api/email').status_code,403)
 def test_empty_prompt_rejected(self):self.assertEqual(self.client.post('/api/tasks',json={'prompt':''}).status_code,422)

class TestExternalResponse(unittest.TestCase):
 def test_empty_success_response(self):
  from unittest.mock import patch
  import asyncio,httpx
  class Client:
   async def __aenter__(self):return self
   async def __aexit__(self,*args):pass
   async def request(self,*args,**kwargs):return httpx.Response(204,content=b'')
  with patch.object(app.httpx,'AsyncClient',return_value=Client()):self.assertIsNone(asyncio.run(app.external('https://example.invalid')))
