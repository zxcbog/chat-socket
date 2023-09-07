import datetime
import socket
import threading
import time

#вообще сокет это средство винды, позволяющее отслеживать и отправлять какие-то пакеты по различным сетевым протоколам. в данном случае мы используем TCP протокол, отличающийся тем, что машина, отправившая пакет не ждет ответа обратно, из-за чего в разы повышается скорость работы, но можем понизиться качество отправляемых пакетов.
class Server:
    def __init__(self,
                 ip: str = '127.0.0.1',
                 port: int = 8080
                 ):

        self.ip = ip
        self.port = port
        self.clients = [] #список подключенных клиентов

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #непосредственно сам сервер
        self.server.bind((ip, port))
        print(f'Server listening on {ip}:{port}')
        self.server.listen(0)
        threading.Thread(target=self.connect_handler).start() #создаем отдельный поток на отслеживание пакетов на подключение

    def connect_handler(self):
        print('Waiting for connection...')

        while True:
            client, address = self.server.accept() #программа будет здесь застывать до тех пор, пока не получит пакет на подключение. затем она его обработает и по циклу снова вернется в эту строку

            if client not in self.clients: #если клиента нет в списке клиентов - добавляем
                name = client.recv(1024).decode('utf-8')
                self.clients.append((client, name))
                threading.Thread(target=self.message_handler, args=(client, name, address[0], )).start() #запускаем отдельный поток для отслеживания сообщений конкретного пользователя. т.е. будет создаваться отдельный поток под каждого пользователя(эт плохая практика но выбора нет)
                print(f"{datetime.datetime.now()} | {name} | {address[0]} was connected")
                for client_s in self.clients: #рассылаем всем пользователям инфу о подключении нового человека
                    client_s[0].send(f"{name} was connected!\n".encode('utf-8'))

            time.sleep(1)
    #обработчик входных пакетов (все сообщения пользователей)
    def message_handler(self, client: socket = None,
                        name: str = '',
                        address: str = ''):

        if client is not None:
            while True:
                message = client.recv(1024)

                if message == b'__disconnect': #так создаются команды для создания каких-то действий. в данном случае команда отключения от сервера
                    self.clients.remove((client, name))
                    print(f"{datetime.datetime.now()} | {name} | {address} was disconnected")
                    for actclient in self.clients:
                        actclient[0].send(f"{name} was disconnected\n".encode('utf-8'))
                    break
                print(f"{datetime.datetime.now()} | {message.decode('utf-8')}")
                for client_s in self.clients:
                    if client_s[0] != client:
                        client_s[0].send(message)

                time.sleep(1)


s = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0] #берет айпи компа и сохраняет его(не помню точно какой, но на моем компе он берет локальный айпи, вероятно в аудитории будет работать точно также. если не будет, то просто замени эту строчку на ip = "Ipv4 из командной строки")
s.close()
server = Server(
    ip,
    8080
)
