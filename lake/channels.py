"""单个查询的来源游标，独立记录消费和关闭。"""
from copy import deepcopy
from .storage import digest

class Source:
    def __init__(self,rows,page_size=2):
        if page_size<1:raise ValueError('页大小非法')
        self.rows=deepcopy(rows);self.page_size=page_size;self.digest=digest(rows);self.events=[];self.n=0
    def open(self,expected_digest):
        if expected_digest!=self.digest:raise ValueError('来源版本不符')
        self.n+=1;c=Cursor(self,self.n);self.events.append({'op':'open','cursor':c.id});return c

class Cursor:
    def __init__(self,source,ident):self.source=source;self.id=ident;self.offset=0;self.seq=0;self.closed=False
    def pull(self):
        if self.closed:raise RuntimeError('游标已关闭')
        s=self.source;rows=deepcopy(s.rows[self.offset:self.offset+s.page_size]);self.offset+=len(rows)
        p={'seq':self.seq,'rows':rows,'digest':digest(rows),'complete':self.offset==len(s.rows)};self.seq+=1
        s.events.append({'op':'pull','cursor':self.id,'seq':p['seq'],'rows':len(rows)});return p
    def close(self):
        if not self.closed:self.source.events.append({'op':'close','cursor':self.id});self.closed=True
