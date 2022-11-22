from fastapi import FastAPI
from zk import ZK, const

app = FastAPI()


@app.get("/connect")
async def connect_device():
    zk = ZK('192.168.5.46', port=4370, timeout=5, password=0, force_udp=False, ommit_ping=False)
    conn = zk.connect()
    attendances = conn.get_attendance()
    return {'message': 'Connected'}

