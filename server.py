import tkinter as tk
import socket
import threading
import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from PIL import Image, ImageTk
import time
import datetime
from ttkbootstrap.scrolled import ScrolledFrame
from cryptography.fernet import Fernet

HOST = '0.0.0.0'
PORT = 8888

class application(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master=master
        self.place()
        self.style_obj = ttk.Style('darkly')
        self.username = 'Server'
        self.key = b'2vZ6L9g3UtU-vv6tZnJLRJxIVWq6jBo0eImEpVfepNY='
    
        # Create a Socket object
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((HOST, PORT))
        self.s.listen()

        # Define the client list and lock object
        self.clients = []
        self.clients_lock = threading.Lock()

        # Create a thread to accept connection of clients
        self.accept_thread = threading.Thread(target=self.accept_clients)
        self.accept_thread.start()

        # Save the user data
        self.rowdata = [
            ('Andy', 'Online')  # Example data
        ]

        self.create_main_frame()
        self.create_text_board()
        # self.create_userlist()


    def create_main_frame(self):
        '''Create the main frame of chat room, the '''

        self.frame_main = ttk.Frame(self.master, width=800, height=600, bootstyle="info")
        self.frame_main.place(x=0, y=0)

        self.frame_message = ttk.Frame(self.frame_main, width=600, height=600, bootstyle="success")
        self.frame_message.place(x=0, y=0)

        self.frame_recv = ttk.Frame(self.frame_message, width=600, height=400, bootstyle="primary")
        self.frame_recv.place(x=0, y=0)

        self.frame_send = ttk.Frame(self.frame_message, width=600, height=200)
        self.frame_send.place(x=0, y=400)

        self.frame_userlist = ttk.Frame(self.frame_main, width=200, height=600, bootstyle="success")
        self.frame_userlist.place(x=600, y=0)
        
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


    def send_message(self):
        time_now = datetime.datetime.now().strftime("%H:%M:%S")
        today = datetime.date.today()
        time_stampe = str(today) + ' ' + str(time_now)

        send_message = self.scrollText_send.get('0.0', tk.END)
        send_message = send_message + '^' + time_stampe + '^' + self.username
        self.scrollText_send.delete('0.0', tk.END)
        message_encrypted = self.encrypt(send_message)

        self.insert_message(send_message)
        
        # Send messages to all clients
        with self.clients_lock:
            for client in self.clients:
                # client.send(send_message.encode())
                client.send(message_encrypted)


    def accept_clients(self):
        '''Function to accept clients' connection
        '''

        while True:
            client_socket, client_address = self.s.accept()
            # Create a thread to handle clients
            client_thread_thread = threading.Thread(target=self.client_thread, args=(client_socket,))
            client_thread_thread.start()


    def client_thread(self, client_socket):
        '''Client thread function
        '''

        # Add client to the client list
        with self.clients_lock:
            self.clients.append(client_socket)
            # for client in self.clients:
            #     self.rowdata.append(client.getpeername())

        # self.dt.destroy()
        # self.create_userlist()

        while True:
            try:
                message = client_socket.recv(1024)
                message_decode = self.decrypt(message)
                # Add new message to message box将接收到的消息添加到消息框
                self.insert_message(message=message_decode)
                # Send new message to all clients
                with self.clients_lock:
                    for client in self.clients:
                        client.send(message)
            except Exception as error:
                # When there are some wrong, remove client from the client list
                with self.clients_lock:
                    self.clients.remove(client_socket)
                    print(error)
                    print('Error! Client has been closed')
                break


    def insert_message(self, message):
        '''Insert message to message board
        '''

        time_stamp = ''
        message_content = ''
        user = ''
        try:
            mess_list = message.split('^')
            message_content = mess_list[0]
            time_stamp = mess_list[1]
            user = mess_list[2]
            self.scrollText_record.insert(tk.END, '\n')
            self.scrollText_record.insert(tk.END, time_stamp+' '+user+' Say:\n')
            self.scrollText_record.insert(tk.END, message_content)
            self.scrollText_record.insert(tk.END, '--------------')
            self.scrollText_record.insert(tk.END, '\n')
        except Exception as error:
            self.scrollText_record.insert(tk.END, '\n')
            self.scrollText_record.insert(tk.END, time_stamp+'\n')
            self.scrollText_record.insert(tk.END, message_content)
            self.scrollText_record.insert(tk.END, '--------------')
            self.scrollText_record.insert(tk.END, '\n')


    def create_userlist(self):
        '''Create user list'''

        self.colname = [
            "User Name",
            {"text": "Status", "stretch": False}
        ]

        self.rowdata = [
            ('Andy', 'Online')  # Example data
        ]
        
        self.dt = Tableview(
            master=self.frame_userlist,
            coldata=self.colname,
            rowdata=self.rowdata,
            paginated=True,
            searchable=True
        )
        self.dt.place(x=0, y=0, width=200, height=600, bordermode='ignore')
    
    # Close the connection and destroy ttk window
    def close_connection(self):
        self.s.close()
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


if __name__=='__main__':
    window_w = 800
    window_h = 600

    root = ttk.Window(alpha=0.9)
    root.attributes("-toolwindow", 0)

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    x = int(screen_w/2 - window_w/2)
    y = int(screen_h/2 - window_h/2)

    root.geometry(f"{window_w}x{window_h}+{x}+{y}")

    root.geometry('800x600')
    root.title('Chat Room Server')
    # root.resizable(False, False)
    app=application(root)
    root.mainloop()