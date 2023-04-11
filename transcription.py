import re
from pyannote.audio import Pipeline
from pydub import AudioSegment
import whisper

import config as cfg

def millisec(timeStr):
  spl = timeStr.split(":")
  s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
  return s

def get_whisper_result(src):
    model = whisper.load_model('small')
    audio = whisper.load_audio(src)
    options = {'language': 'ru', 'task': 'transcribe', 'fp16': False, 'word_timestamps': True}
    result = whisper.transcribe(model, audio, **options)
    sentences, snt, start = [], '', None
    for segment in result['segments']:
      for i in segment['words']:
        snt += i['word']
        if not start:
          start = int(i['start']*1000)
        if i['word'][-1] in ('.', '?', '!'):
          sentences.append([start, snt])
          snt, start = '', None
    return sentences

def get_transcription(src):
  # convert to wav
  audio = AudioSegment.from_file(src, format=src.split('.')[-1])
  audio.export(src+'.wav', format='wav')
  # diarization
  pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', 
                                      use_auth_token=cfg.hf_token)
  dz = str(pipeline({'uri': 'blabal', 'audio': src+'.wav'})).split('\n')
  wsp = get_whisper_result(src)
  dzList = []
  for l in dz:
    end =  int(millisec(tuple(re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=l))[1]))
    name = '[Первый спикер]' if not re.findall('SPEAKER_01', string=l) else '[Второй спикер]'
    dzList.append([end, name])
  text = []
  for sent in wsp:
    for dz in dzList:
      if dz[0] >= sent[0] and dz[1] and sent[1]:
        text.append(str(dz[1] + sent[1]))
        break
  text = '\n'.join(text)
  with open(src.split('.')[0] + '.txt', 'w') as text_file:
    text_file.write(text)
  return text


if __name__ == '__main__':
  rezult = get_transcription('speech.m4a')
  print(rezult)
