import tkinter as tk
from tkinter import messagebox
import socket
import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from PIL import Image, ImageTk
import time
import datetime
from ttkbootstrap.scrolled import ScrolledFrame
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet



class application(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master=master
        self.place()
        self.style_obj = ttk.Style('darkly')
        self.key = b'2vZ6L9g3UtU-vv6tZnJLRJxIVWq6jBo0eImEpVfepNY='
        self.HOST = '127.0.0.1'
        self.PORT = 8888
        self.username = ''

        self.edit_setting()

        self.create_main_frame()
        self.create_text_board()
    
        # 创建一个Socket对象
        try:
            self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.c.connect((self.HOST, self.PORT))
        except Exception as e:
            pass


    def create_main_frame(self):
        self.frame_main = ttk.Frame(self.master, width=800, height=600, bootstyle="info")
        self.frame_main.place(x=0, y=0)

        self.frame_message = ttk.Frame(self.frame_main, width=600, height=600, bootstyle="success")
        self.frame_message.place(x=0, y=0)

        self.frame_recv = ttk.Frame(self.frame_message, width=600, height=400, bootstyle="primary")
        self.frame_recv.place(x=0, y=0)

        self.frame_send = ttk.Frame(self.frame_message, width=600, height=200)
        self.frame_send.place(x=0, y=400)

    
    def edit_setting(self):
        '''Edit user's username and server IP
        '''
        
        if self.username == '':
            self.win_setting = tk.Toplevel()
            self.win_setting.wm_attributes('-topmost', 1)
            self.win_setting.attributes('-toolwindow', 3)
            width = 300
            height = 200
            # get information of monitor
            screenwidth = self.win_setting.winfo_screenwidth()
            screenheight = self.win_setting.winfo_screenheight()
            size_geo = '%dx%d+%d+%d' % (width, height, (screenwidth-width)/3, (screenheight-height)/3)
            self.win_setting.geometry(size_geo)

            self.win_setting.title('Setting')

            self.win_setting_frame_root = ttk.Frame(self.win_setting, width=300, height=200)
            self.entry_server_ip_label = ttk.Label(self.win_setting_frame_root, text='Server IP: ')
            self.entry_server_ip = ttk.Entry(self.win_setting_frame_root)
            self.entry_server_username_label = ttk.Label(self.win_setting_frame_root, text='Username:  ')
            self.entry_username = ttk.Entry(self.win_setting_frame_root)
            self.button_submit = ttk.Button(self.win_setting_frame_root, text='Submit', command=self.set_username)

            self.win_setting_frame_root.place(x=0, y=0)
            self.entry_server_ip_label.place(x=15, y=10)
            self.entry_server_ip.place(x=80, y=5, width=200)
            self.entry_server_username_label.place(x=15, y=45)
            self.entry_username.place(x=80, y=45, width=200)
            self.button_submit.place(x=15, y=85, width=80)
        else:
            pass

    
    def check_setting(self):
        '''Check if user has set his username and server IP'''
        if self.username == '':
            return False
        else:
            return True


    def create_text_board(self):
        self.scrollText_record = ttk.ScrolledText(self.frame_recv, font=("黑体", 12))
        self.scrollText_record.place(x=0, y=0, width=600, height=400, bordermode='inside')

        self.scrollText_send = ttk.ScrolledText(self.frame_send, font=("黑体", 12))
        self.scrollText_send.place(x=0, y=0, width=600, height=160, bordermode='inside')
        self.scrollText_send.bind("<Return>", lambda event: self.send_message())

        self.button_send = ttk.Button(self.frame_send, text='Send', bootstyle='success', command=self.send_message)
        self.button_send.place(x=529, y=165)

        self.button_close = ttk.Button(self.frame_send, text='Close', bootstyle='success', command=self.close_connection)
        self.button_close.place(x=459, y=165)

    # 定义发送消息的函数
    def send_message(self):
        set_flag = self.check_setting()

        if set_flag == True:
            time_now = datetime.datetime.now().strftime("%H:%M:%S")
            today = datetime.date.today()
            time_stampe = str(today) + ' ' + str(time_now)

            message = self.scrollText_send.get('0.0', tk.END)
            message = message + '^' + time_stampe + '^' + self.username
            message_encrypted = self.encrypt(str(message))
            # 发送消息到服务器
            print('sending: ' + str(message_encrypted))
            self.c.send(message_encrypted)
            # 清空文本框
            self.scrollText_send.delete('0.0', tk.END)
        else:
            self.edit_setting()

    def receive_message(self):
        while True:
            message = self.c.recv(1024).decode()
            message_decode = self.decrypt(message)
            print(message)
            self.insert_message(message_decode)
        
    # Insert message to message board
    def insert_message(self, message):
        print(message)
        mess_list = message.split('^')
        message_content = mess_list[0]
        time_stamp = mess_list[1]
        user = mess_list[2]
        self.scrollText_record.insert(tk.END, '\n')
        self.scrollText_record.insert(tk.END, time_stamp+' '+user+' Say:\n')
        self.scrollText_record.insert(tk.END, '\n')
        self.scrollText_record.insert(tk.END, message_content)
        self.scrollText_record.insert(tk.END, '--------------')
        self.scrollText_record.insert(tk.END, '\n')

    def close_connection(self):
        self.c.close()
        self.master.destroy()

    # Encrypt message
    def encrypt(self, data):
        cipher_suite = Fernet(self.key)

        return cipher_suite.encrypt(data.encode())

    # Decode
    def decrypt(self, encrypted_data):
        cipher_suite = Fernet(self.key)
        decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
        
        return decrypted_data

    
    def set_username(self):
        host = str(self.entry_server_ip.get())
        username = self.entry_username.get()
        print(host)

        if username != '':
            self.username = username

        if host == '':
            self.HOST = '127.0.0.1'
            messagebox.showerror('Null server ip', 'Default server ip has been set !')
        else:
            self.HOST = host

        if host != '127.0.0.1' and host != '':
            self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.c.connect((self.HOST, self.PORT))
        
        # 创建一个线程来接收消息
        self.receive_thread = threading.Thread(target=self.receive_message)
        self.receive_thread.start()

        self.win_setting.destroy()


if __name__=='__main__':
    root = ttk.Window(alpha=0.9)
    root.geometry('800x600')
    root.title('Chat Room')
    # root.resizable(False, False)
    app=application(root)
    root.mainloop()