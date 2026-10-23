"""Original V860 ARM TTS; isolated process with an external deadline."""
import sys,struct,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))
from unicorn import *
from unicorn.arm_const import *
raw=(ROOT/'firmware.bin').read_bytes()
base=0xb10
h=struct.unpack_from('<16sHHIIIIIHHHHHH',raw,base)
segments=[struct.unpack_from('<8I',raw,base+h[5]+i*h[9]) for i in range(h[10])]

def synthesize(text,language='enus',rate=50,pitch=50):
 if language not in ('enus','esmx'):raise ValueError('Unknown language')
 if not text or len(text)>200 or '\0' in text:raise ValueError('Invalid text length')
 if not 0<=rate<=100 or not 0<=pitch<=100:raise ValueError('Invalid settings')
 u=Uc(UC_ARCH_ARM,UC_MODE_ARM);u.mem_map(0,0x8000000)
 for t,o,v,p,n,ms,f,al in segments:
  if v<0x8000000:u.mem_write(v,raw[base+o:base+o+n])
 from collections import deque
 trace=deque(maxlen=100)
 # Per-block tracing is disabled for normal synthesis speed.
 heap=0x5000000;allocs={};log=[]
 def ret(value=0):u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def hook(u,a,size,user):
  nonlocal heap
  if a in (0x2989468,0x29895b4,0x29917b4):
   n=u.reg_read(UC_ARM_REG_R0);assert n<0x1000000
   p=heap+8;heap+=(n+31)&~7;assert heap<0x7000000
   u.mem_write(p-8,struct.pack('<II',n,0));allocs[p]=n;ret(p)
  elif a==0x29894f4:ret()
  elif a==0x1a21268:
   for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2):
    p=u.reg_read(r)
    if p:u.mem_write(p,bytes(4))
   ret()
  elif a==0x1f57284:
   args=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   raise RuntimeError('Native assertion: '+str(args))
 def invalid(u,access,a,size,value,user):return False
 for a in [0x2989468,0x29895b4,0x29917b4,0x29894f4,0x1f57284,0x1a21268]:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
 u.hook_add(UC_HOOK_MEM_INVALID,invalid)
 def call(addr,*args):
  sp=0x7fe0000
  for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(r,v)
  for i,v in enumerate(args[4:]):u.mem_write(sp+4*i,struct.pack('<I',v & 0xffffffff))
  u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x7fff000)
  try:u.emu_start(addr,0x7fff000)
  except UcError as e:raise RuntimeError('ARM execution failed') from e
  assert u.reg_read(UC_ARM_REG_PC)==0x7fff000, 'Native call did not finish'
  return u.reg_read(UC_ARM_REG_R0)

 u.mem_write(0x7000000,language.encode()+b'\0')
 if call(0x1eef28d,0x7000000,0x1c,0x1c,8000,0x7001000,0x7002000):raise RuntimeError('Voice initialization failed')
 ctx=struct.unpack('<I',u.mem_read(0x7002000,4))[0]
 if not ctx:raise RuntimeError('Missing voice context')
 fmt=call(0x1f23b79,ctx);fps=call(0x1f51545,fmt)
 if fps!=16000:raise RuntimeError('Unexpected PCM rate')
 u.mem_write(0x7003000,(text+'\0').encode('utf-16-le'))
 speed=round(100*2**((rate-50)/50))
 pitch_shift=0  # Final native argument is gain, not pitch.
 if call(0x1ef8125,ctx,0x7003000,fmt,fps,speed,pitch_shift):raise RuntimeError('Cannot start speech')
 model=struct.unpack('<I',u.mem_read(ctx+0x14,4))[0]
 pending=bytearray()
 for i in range(30000):
  status=call(0x1eeae09,model,16000,0x7100000,0x7004000)
  n=struct.unpack('<I',u.mem_read(0x7004000,4))[0]
  if n>16000:raise RuntimeError('Invalid PCM size')
  if n:pending.extend(u.mem_read(0x7100000,n*2))
  if len(pending)>=2048:
   yield bytes(pending);pending.clear()
  if status==3:
   if pending:yield bytes(pending)
   return
  if status not in (0,5,6):raise RuntimeError('Synthesis status '+str(status))
 raise RuntimeError('Speech too long')

if __name__=='__main__':
 request=json.loads(sys.stdin.buffer.read(8192))
 for pcm in synthesize(request['text'],request.get('language','enus'),int(request.get('rate',50)),int(request.get('pitch',50))):
  sys.stdout.buffer.write(struct.pack('<I',len(pcm))+pcm);sys.stdout.buffer.flush()
 sys.stdout.buffer.write(struct.pack('<I',0));sys.stdout.buffer.flush()
