import torch, torchaudio as ta, sys
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
m=ChatterboxMultilingualTTS.from_pretrained(device='cpu')
lines=[
 ("01_intro","NTT 그룹, 이름은 다 같아도 연봉도 잔업도 회사마다 꽤 달라요. 오늘은 큰 회사 다섯 곳, 덜 알려진 자회사 다섯 곳, 그리고 지역 회사 세 곳 순서로 소개할게요."),
 ("02_big","먼저 큰 회사 다섯 곳입니다. 화면 캡처해 두세요."),
 ("03_sub","다음은 이름은 낯설어도 대우는 그룹 수준인 자회사 다섯 곳."),
 ("04_local","마지막은 지역 근무가 가능한 회사 세 곳이에요."),
 ("05_end","어디가 궁금한지 댓글로 알려주세요. 다음은 미쓰비시 그룹입니다."),
]
for ref,tag,kw in [("밝은 친근.wav","bright",dict(exaggeration=0.7,cfg_weight=0.4)),("중간 침착.wav","calm",dict(exaggeration=0.45,cfg_weight=0.5)),("낮음 성우.wav","low",dict(exaggeration=0.35,cfg_weight=0.55))]:
    for name,text in lines:
        w=m.generate(text,language_id='ko',audio_prompt_path=ref,**kw)
        ta.save(f'out/{tag}_{name}.wav',w,m.sr)
        print(tag,name,flush=True)
