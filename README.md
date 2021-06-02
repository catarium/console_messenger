# Консольный мессенджер
##
## Клиент
### Перейдите в директорию клиента
```
cd client
```
### Установите зависимости
```
pip install -r requirements.txt
```
### Перейдите в директорию выше
```
cd ..
```
### Запустите client_tui.py
```
python client_tui.py
```
## Сервер
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
