import os, sys, time
os.environ['HF_HUB_OFFLINE']='1'; os.environ['PYTHONUTF8']='1'
import torch, soundfile as sf
from qwen_tts import Qwen3TTSModel
from script import LINES
P='/root/.cache/huggingface/hub/models--Qwen--Qwen3-TTS-12Hz-0.6B-Base/snapshots/5d83992436eae1d760afd27aff78a71d676296fc'
m=Qwen3TTSModel.from_pretrained(P,device_map='cpu',dtype=torch.float32)
os.makedirs('lines',exist_ok=True)
for k,t in LINES:
    if os.path.exists(f'lines/{k}.wav'): continue
    t0=time.time()
    w,sr=m.generate_voice_clone(text=t,language='Japanese',ref_audio='ref15.wav',x_vector_only_mode=True)
    sf.write(f'lines/{k}.wav',w[0],sr); print(k,round(len(w[0])/sr,1),'s',round(time.time()-t0),'sec',flush=True)
print('ALL DONE')
