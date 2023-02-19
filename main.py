import os
import sys
import json
import base64
import pyaudio
import asyncio
import textblob
import requests
import websockets
from PyQt6 import QtWidgets, uic


# CONFIGURATION

class Config:
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    FS = 3200
    ASSEMBLY_AI_API_KEY = os.environ['ASSEMBLY_AI_API_KEY']
    ENDPOINT_TRANSCRIPT = 'wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000'
    ENDPOINT_SERVER = 'http://127.0.0.1:5000/endpoint'


# AUDIO PROCESSING

async def send_recv(stream):
    async with websockets.connect(
            Config.ENDPOINT_TRANSCRIPT,
            extra_headers=(("Authorization", Config.ASSEMBLY_AI_API_KEY),),
            ping_interval=10,
            ping_timeout=40,
    ) as ws:
        await asyncio.sleep(0.1)
        session = await ws.recv()

        async def send():
            while True:
                try:
                    data = stream.read(Config.FS, exception_on_overflow=False)
                    data = base64.b64encode(data).decode('utf-8')
                    Config.DATA = str(data)
                    json_data = json.dumps({
                        'audio_data': Config.DATA,
                    })
                    await ws.send(json_data)
                except websockets.ConnectionClosed as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, 'ERROR'
                await asyncio.sleep(0.001)
            return True

        async def recv():
            while True:
                try:
                    res = json.loads(await ws.recv())
                    print(res)
                    sentiment = textblob.TextBlob(res['text']).sentiment.polarity
                    requests.post(
                        Config.ENDPOINT_SERVER,
                        json={
                            'sentiment': sentiment
                        },
                        headers={
                            'Content-Type': 'application/json'
                        }
                    )
                except websockets.ConnectionClosed as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, 'ERROR'
        send_res, recv_res = await asyncio.gather(send(), recv())


def record(is_recording):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=Config.FORMAT,
        channels=Config.CHANNELS,
        rate=Config.RATE,
        input=True,
        frames_per_buffer=Config.FS
    )
    asyncio.run(send_recv(stream))


# GUI

class FluxAnalyzer(QtWidgets.QMainWindow):
    def __init__(self):
        super(FluxAnalyzer, self).__init__()
        uic.loadUi('main.ui', self)
        self.show()
        self.record.clicked.connect(record)


# MAIN

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = FluxAnalyzer()
    app.exec()


if __name__ == '__main__':
    main()
