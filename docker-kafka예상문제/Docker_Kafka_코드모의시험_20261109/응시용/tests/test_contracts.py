"""Offline contract tests. No broker, network or installed kafka-python required."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace as NS

BASE = Path(sys.argv.pop(1) if len(sys.argv)>1 else "tasks")
def load(name):
    spec=importlib.util.spec_from_file_location(name, BASE/(name+".py"))
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
q8,q9,q10,q11=[load(n) for n in ["q08_admin","q09_producer","q10_consumer","q11_pipeline"]]
class Topic:
    def __init__(self, name, num_partitions, replication_factor):
        self.name=name; self.num_partitions=num_partitions; self.replication_factor=replication_factor
admin_module=types.ModuleType("kafka.admin"); admin_module.NewTopic=Topic
kafka_module=types.ModuleType("kafka"); kafka_module.admin=admin_module
sys.modules["kafka"]=kafka_module; sys.modules["kafka.admin"]=admin_module
class Admin:
    def __init__(self, existing=(), fail=False):
        self.existing=set(existing); self.calls=[]; self.fail=fail
    def list_topics(self): return list(self.existing)
    def create_topics(self, topics):
        if self.fail: raise RuntimeError("admin failed")
        self.calls.append(topics); self.existing.update(t.name for t in topics)
class Producer:
    def __init__(self, fail=False): self.events=[]; self.fail=fail
    def send(self, topic, **kwargs):
        self.events.append(("send",topic,kwargs))
        owner=self
        class Future:
            def get(self,timeout):
                owner.events.append(("get",timeout))
                if owner.fail: raise RuntimeError("send failed")
        return Future()
    def flush(self): self.events.append(("flush",))
def message(value,key=None,partition=0,offset=0):
    return NS(value=value,key=key,partition=partition,offset=offset)
class ExamTests(unittest.TestCase):
    def test_admin_empty(self):
        a=Admin(); self.assertEqual(q8.prepare_topics(a),["mk-input","mk-orders","mk-output"])
        self.assertEqual({t.name:(t.num_partitions,t.replication_factor) for t in a.calls[0]},
                         {"mk-orders":(3,1),"mk-input":(1,1),"mk-output":(1,1)})
    def test_admin_partial(self):
        a=Admin(["mk-input","unrelated"]); self.assertEqual(q8.prepare_topics(a),["mk-orders","mk-output"])
        self.assertIn("unrelated",a.existing)
    def test_admin_repeat(self):
        a=Admin(); q8.prepare_topics(a); self.assertEqual(q8.prepare_topics(a),[]); self.assertEqual(len(a.calls),1)
    def test_admin_all_exist(self):
        a=Admin(q8.TOPICS); self.assertEqual(q8.prepare_topics(a),[]); self.assertEqual(a.calls,[])
    def test_admin_error(self):
        with self.assertRaises(RuntimeError): q8.prepare_topics(Admin(fail=True))
    def test_producer_options(self):
        opts=q9.make_producer(lambda **kw:kw,"example:1234")
        self.assertEqual(opts['bootstrap_servers'],'example:1234')
        self.assertEqual(opts['key_serializer']('서울'),'서울'.encode())
        self.assertEqual(opts['value_serializer']('배송'),'배송'.encode())
        self.assertEqual(opts['value_serializer'](''),b'')
    def test_send_normal(self):
        p=Producer(); self.assertEqual(q9.send_records(p,[{'store':'A','text':'one'},{'store':'A','text':'two'}]),2)
        self.assertEqual(p.events,[("send","mk-orders",{'key':'A','value':'one'}),("get",10),
                                   ("send","mk-orders",{'key':'A','value':'two'}),("get",10),("flush",)])
    def test_send_empty_list(self):
        p=Producer(); self.assertEqual(q9.send_records(p,[]),0); self.assertEqual(p.events,[("flush",)])
    def test_send_empty_value(self):
        p=Producer(); self.assertEqual(q9.send_records(p,[{'store':'A','text':''}]),1)
        self.assertEqual(p.events[0][2]['value'],'')
    def test_send_error(self):
        with self.assertRaises(RuntimeError): q9.send_records(Producer(True),[{'store':'A','text':'x'}])
    def test_consumer_options(self):
        args,kw=q10.make_consumer(lambda *a,**kw:(a,kw),'other','server:9','group-x')
        self.assertEqual(args,('other',)); self.assertEqual(kw,dict(bootstrap_servers='server:9',
            group_id='group-x',auto_offset_reset='earliest',enable_auto_commit=True,consumer_timeout_ms=10000))
    def test_consume_unicode(self):
        self.assertEqual(q10.collect([message('배송'.encode(),'서울'.encode(),2,8)]),
                         [dict(key='서울',value='배송',partition=2,offset=8)])
    def test_consume_null_key_empty_value(self):
        self.assertEqual(q10.collect([message(b'')]),[dict(key=None,value='',partition=0,offset=0)])
    def test_consume_empty(self): self.assertEqual(q10.collect([]),[])
    def test_consume_bad_value(self):
        with self.assertRaises(UnicodeDecodeError): q10.collect([message(b'\xff')])
    def test_consume_bad_key(self):
        with self.assertRaises(UnicodeDecodeError): q10.collect([message(b'ok',b'\xff')])
    def test_transform_normal(self): self.assertEqual(q11.transform(b' coffee '),'COFFEE')
    def test_transform_unicode(self): self.assertEqual(q11.transform(' 한글 '.encode()),'한글')
    def test_transform_empty(self): self.assertIsNone(q11.transform(b''))
    def test_transform_spaces(self): self.assertIsNone(q11.transform(b' \t\n '))
    def test_transform_bad_utf8(self):
        with self.assertRaises(UnicodeDecodeError): q11.transform(b'\xff')
    def test_relay_normal_and_skip(self):
        p=Producer(); rows=[message(x.encode()) for x in [' coffee ','tea','   ','한글']]
        self.assertEqual(q11.relay(rows,p),3)
        self.assertEqual([e for e in p.events if e[0]=='send'],
                         [('send','mk-output',{'value':v}) for v in ['COFFEE','TEA','한글']])
        self.assertEqual([e for e in p.events if e[0]=='get'],[('get',10)]*3)
        self.assertEqual(p.events[-1],('flush',))
    def test_relay_empty(self):
        p=Producer(); self.assertEqual(q11.relay([],p),0); self.assertEqual(p.events,[('flush',)])
    def test_relay_all_blank(self):
        p=Producer(); self.assertEqual(q11.relay([message(b' '),message(b'')],p),0)
        self.assertEqual(p.events,[('flush',)])
    def test_relay_send_error(self):
        with self.assertRaises(RuntimeError): q11.relay([message(b'x')],Producer(True))
    def test_relay_decode_error(self):
        p=Producer()
        with self.assertRaises(UnicodeDecodeError): q11.relay([message(b'\xff')],p)
        self.assertFalse(any(e[0]=='send' for e in p.events))
if __name__=='__main__': unittest.main(verbosity=2)
