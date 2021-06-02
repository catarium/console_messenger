# Консольный мессенджер
- [Клиент](#client)
- [Сервер](#server)
## Клиент <a name="client">
### Перейдите в директорию клиента
```
cd client
```
### Установите зависимости
```
pip install -r requirements.txt
```
### Укажите хост в config.json
```
{
    "url": "например http://127.0.0.1:8000",
    "websocket_url": "например ws://127.0.0.1:8000",
    "token": "",
    "lang": "ru"
}
```
### Перейдите в директорию выше
```
cd ..
```
### Запустите client_tui.py
```
python client_tui.py
```
## Сервер <a name="server">
### Перейдите в директорию сервера
```
cd server
```
### Установите зависимости
```
pip install -r requirements.txt
```
### Перейдите в директорию выше
```
cd ..
```
### Запустите start_server.py через uvicorn
```
uvicorn start_server:app --reload
```
