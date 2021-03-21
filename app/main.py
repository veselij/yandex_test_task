import uvicorn
from server.constant import BIND_IP, PORT

if __name__ == '__main__':
    uvicorn.run('server.app:app', host=BIND_IP, port=PORT, reload=True)
