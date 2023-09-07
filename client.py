import socket
import threading
import tkinter.messagebox
from tkinter import *


class MyError(Exception):
	def __init__(self, text):
		self.txt = text


class Client:
	def __init__(self):
		self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# GUI создаем интерфейс на ткинтере
		self.tk = Tk()
		self.text = StringVar()
		self.name = StringVar()
		self.name.set('YourNickName') #сюда можно вставить любое начальное имя
		self.text.set('')
		ip = StringVar()
		ip.set('IP')
		port = StringVar()
		port.set("PORT")
		self.tk.title('chat')
		self.tk.geometry('500x400')
		self.tk.resizable(False, False)
		self.log = Text(self.tk)
		self.serverIp = Entry(self.tk, textvariable=ip)
		self.serverPort = Entry(self.tk, textvariable=port)
		self.connect = Button(self.tk, text='Connect', command=self.connect)
		self.nick = Entry(self.tk, textvariable=self.name)
		self.msg = Entry(self.tk, textvariable=self.text, state='disabled')
		self.msg.pack(side='bottom', fill='x')
		self.nick.pack(side='bottom', fill='x')
		self.serverIp.pack(side='top', fill='x')
		self.serverPort.pack(side='top', fill='x')
		self.connect.pack(side='top', fill='x')
		self.log.pack(side='top', fill='both')
		#
		self.msg.bind('<Return>', self.sendproc)
		self.tk.protocol("WM_DELETE_WINDOW", self.closeconn)
		self.msg.focus_set()

		self.tk.mainloop()
	#процедура подключения
	def connect(self):
		try:
			if self.serverIp.get().count('.') == 3 and int(self.serverPort.get()) > 1024 and self.name.get():
				self.client_sock.connect((self.serverIp.get(), int(self.serverPort.get())))
				self.client_sock.send(self.name.get().encode('utf-8'))
				self.nick.configure(state='disabled')
				self.msg.configure(state='normal')
				self.serverIp.configure(state='disabled')
				self.serverPort.configure(state='disabled')
				self.connect.configure(state='disabled')
				threading.Thread(target=self.getmsg, args=(self.log, self.client_sock,), daemon=True).start()#создаем отдельный поток для отслеживания получаемых сообщений
			else:
				raise MyError("Ошибка входных данных")
		except Exception as ex:
			tkinter.messagebox.showwarning("Ошибка", str(ex))
	#процедура получения сообщений от сервера
	def getmsg(self, log, client_sock):
		while True:
			msg = client_sock.recv(1024)
			log.insert(END, f"{msg.decode('utf-8')}")
			log.yview_scroll(500, "units")
	#процедура отправки сообщений серверу
	def sendproc(self, event):
		if self.text.get():
			msg = self.name.get() + ": " + self.text.get() + '\n'
			self.client_sock.send(msg.encode('utf-8'))
			self.log.insert(END, f"You: {self.text.get()}\n")
			self.text.set('')
			self.log.yview_scroll(500, "units")
	#процедура отключения от сервера
	def closeconn(self):
		try:
			self.client_sock.send('__disconnect'.encode('utf-8'))
			self.tk.destroy()
		except:
			self.tk.destroy()


if __name__ == '__main__':
	client = Client()
