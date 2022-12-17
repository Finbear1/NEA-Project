import pandas as pd
import requests
from bs4 import BeautifulSoup
import sqlite3
import urllib3
from tkinter import *
from tkinter import messagebox
from time import time

#code to bypass verification when web scraping
urllib3.disable_warnings()

#connection to database
conn = sqlite3.connect('game.db')
cursor1 = conn.cursor()
cursor2 = conn.cursor()

#creation of tables

conn.execute("""CREATE TABLE IF NOT EXISTS ACCOUNT
            (USERNAME     TEXT       ,
            PASSWORD      TEXT       NOT NULL);""")

conn.commit()

conn.execute("""CREATE TABLE IF NOT EXISTS STOCKS
            (USERNAME     TEXT      NOT NULL,
            STOCK         TEXT      NOT NULL,
            TOTAL         INT       NOT NULL,
            VALUE         FLOAT(10) NOT NULL);""")

conn.commit()

conn.execute("""CREATE TABLE IF NOT EXISTS VALUE
            (USERNAME    TEXT       ,
            WALLET       INT        );""")

conn.commit()
            
#Main Interface

def main():
    global user_menu
    global wallet
    user_menu = Tk()
    user_menu.geometry("1280x720")
    user_menu.title("Portfolio")
    canvas=Canvas(user_menu, width=1280, height=720)
    canvas.pack()

    #Buy Button
    
    def buy_clicked(event):
        global stockchoice
        global total_entry
        global buy_gui
        buy_gui = Tk()
        buy_gui.geometry("300x200")
        buy_gui.title("Buy Stock")
        buy_gui.configure(bg="#333333")
        label1 = Label(buy_gui, text="Enter Stock:", bg="#333333", fg="white")
        stockchoice = Entry(buy_gui)
        stockchoice.grid(row=3, column=1, sticky=W)
        buy_button1 = Button(buy_gui, text="Confirm", command=add_stock)
        label2 = Label(buy_gui, text="Quantity:", bg="#333333", fg="white")
        total_entry = Entry(buy_gui)
        label1.grid(row=3, column=0)
        label2.grid(row=5, column=0)
        total_entry.grid(row=5, column=1)
        buy_button1.grid(row=3, column=5, columnspan=2)
        
        buy_gui.mainloop()

    #Sell Button
    
    def sell_clicked(event):
        global sell_stockchoice
        global sell_gui
        sell_gui = Tk()
        sell_gui.geometry("300x200")
        sell_gui.title("Sell Stock")
        sell_gui.configure(bg="#333333")
        label1 = Label(sell_gui, text="Enter Stock:", bg="#333333", fg="white")
        sell_stockchoice = Entry(sell_gui)
        sell_stockchoice.grid(row=3, column=1, sticky=W)
        sell_button1 = Button(sell_gui, text="Confirm", command=sell_stock)
        label1.grid(row=3, column=0)
        sell_button1.grid(row=3, column=5, columnspan=2)
        
        sell_gui.mainloop()
        
    #Main structure
    canvas.create_rectangle(0, 0, 300, 100, fill='white')
    canvas.create_rectangle(300, 100, 1280, 720, fill='white')
    canvas.create_rectangle(900, 0, 1280, 720, fill='white')
    buy_buttonBG = canvas.create_rectangle(600, 100, 600, 0, fill='white')
    canvas.create_text(100,40, text=username, font="45")
    
    #Scoreboard widget
    ScoreboardTXT = canvas.create_text(1000, 700, text="View Scoreboard", font="45")
    canvas.tag_bind(ScoreboardTXT, "<Button-1>", scoreboard)
    
    #Log out widget
    exitTXT = canvas.create_text(1100, 700, text="Log out", font="45")
    canvas.tag_bind(exitTXT, "<Button-1>", exit)
    
    #buttons to buy
    buy_buttonTXT = canvas.create_text(450, 40, text="Buy", font="45")
    canvas.tag_bind(buy_buttonBG, "<Button-1>", buy_clicked) 
    canvas.tag_bind(buy_buttonTXT, "<Button-1>", buy_clicked) 
    
    #buttons to sell
    sell_buttonBG = canvas.create_rectangle(600, 100, 600, 0, fill='white')
    sell_buttonTXT = canvas.create_text(750, 40, text="Sell", font="45")
    canvas.tag_bind(sell_buttonTXT, "<Button-1>", sell_clicked)
    
    #wallet widget
    cursor1.execute("SELECT WALLET FROM VALUE WHERE username = ?", [username])
    wallet = cursor1.fetchone()
    wallet_TXT = canvas.create_text(1050, 40, text=("Amount of money left:", wallet) , font="45")
    
    #Display users current stock list
    cursor1.execute("SELECT * FROM STOCKS WHERE username = ?", [username])
    stock_list = cursor1.fetchall()
    temp_stocklist = list(stock_list)
    l_stocklist = []
    for n in temp_stocklist:
        y = list(n)
        l_stocklist.append(y)
    
    for x in range(0, len(l_stocklist)):
        l_stocklist[x].pop(0)
        
    row = 150
    for i in l_stocklist:
        stock_listTXT = canvas.create_text(100, row, text=i, font="45")
        row += 50
    
    

#Login Subroutine

def login_gui():
    gui = Tk()
    gui.geometry("400x150")
    gui.title("Login Page")
    gui.configure(bg="#333333")


    def login():
        global username
        global password
        cursor1.execute("SELECT * FROM ACCOUNT WHERE username = ? AND password = ?", (user_entry.get(), password_entry.get()))
        account = cursor1.fetchone()
        #Verifys if users details exist
        try:
            if user_entry.get() == account[0] and password_entry.get()==account[1]:
                messagebox.showinfo(title="Succesful login", message="You succesfully logged in")
                username = user_entry.get()
                password = password_entry.get()
                gui.destroy()
                main()
            
        except:
            messagebox.showerror(title="Invalid login", message="Invalid login")
        
        #main()
        
    
    #widgets
    login_label = Label(gui, text="Login", bg="#333333", fg="white", font=25)
    label1 = Label(gui, text="Username:", bg="#333333", fg="white")
    user_entry = Entry(gui)
    label2 = Label(gui, text="Password:", bg="#333333", fg="white")
    password_entry = Entry(gui, show="*")
    button1 = Button(gui, text = "Confirm",command=login)

    #grid
    login_label.grid(row=0, column=0, columnspan=2)
    label1.grid(row=1, column=0)
    label2.grid(row=2, column=0)
    user_entry.grid(row=1, column=1)
    password_entry.grid(row=2, column=1)
    button1.grid(row=3, column=1, columnspan=2)

    gui.lift()
    gui.attributes('-topmost',True)
    gui.after_idle(gui.attributes,'-topmost',False)
    gui.mainloop()
    
#Subroutine to create a new account

def create_account():
    create_menu = Tk()
    create_menu.geometry("400x150")
    create_menu.title("Create a new Account")
    create_menu.configure(bg="#333333")
    
    def create():
        conn.execute("""INSERT INTO ACCOUNT (USERNAME,PASSWORD) \
                         VALUES (?,?)
                        """, (user_entry.get(), password_entry.get()))
        conn.execute("""INSERT INTO VALUE (USERNAME, WALLET) VALUES (?,?)""", (user_entry.get(), 5000))
        conn.commit()
        #create_menu.destroy()
        login_gui()
    
    def next1():
        create_menu.destroy()
        login_gui()
        
    #widgets
    create_label = Label(create_menu, text="Create new account", bg="#333333", fg="white", font=25)
    create_label1 = Label(create_menu, text="Username:", bg="#333333", fg="white")
    user_entry = Entry(create_menu)

    create_label2 = Label(create_menu, text="Password:", bg="#333333", fg="white")
    password_entry = Entry(create_menu)

    create_button1 = Button(create_menu, text = "Confirm",command=create)
    next_button = Button(create_menu, text = "Sign in", command=next1)

    #grid
    create_label.grid(row=0, column=0, columnspan=2)
    create_label1.grid(row=1, column=0)
    create_label2.grid(row=2, column=0)
    user_entry.grid(row=1, column=1)
    password_entry.grid(row=2, column=1)
    create_button1.grid(row=3, column=1, columnspan=2)
    next_button.grid(row=5, column=1, columnspan=2)

    create_menu.lift()
    create_menu.attributes('-topmost',True)
    create_menu.after_idle(create_menu.attributes,'-topmost',False)
    create_menu.mainloop()
        
#subroutine to allow users to add stocks to portfolio

def add_stock():
    global stockchoice
    global wallet
    global price
    global total
    stockchoice = str(stockchoice.get())
    total = str(total_entry.get())
    url = 'https://finance.yahoo.com/quote/'+stockchoice+''
    page = requests.get(url, verify=False)
    soup = BeautifulSoup(page.text, 'html.parser')
    name = soup.find('h1', {'class':  'D(ib) Fz(18px)'}).text
    price = soup.find('fin-streamer', {'class': 'Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
    value = float(price) * float(total)
    conn.execute("""INSERT INTO STOCKS (USERNAME, STOCK, TOTAL, VALUE)  VALUES (?,?,?,?)""", (str(username), str(stockchoice), int(total), value))
    conn.commit()
    wallet = float(*wallet) - float(price) * float(total)
    conn.execute("UPDATE VALUE SET WALLET = ? WHERE USERNAME = ?", (wallet, username))
    conn.commit()
    user_menu.withdraw()
    main()
    buy_gui.destroy()
        
    return price, name

def sell_stock():
    global sell_stockchoice
    global wallet
    global price
    sell_stockchoice = str(sell_stockchoice.get())
    cursor1.execute("DELETE FROM STOCKS WHERE USERNAME = ? AND STOCK = ?", (username, sell_stockchoice))
    conn.commit()
    wallet = float(*wallet) + float(price) * float(total)
    conn.execute("UPDATE VALUE SET WALLET = ? WHERE USERNAME = ?", (wallet, username))
    conn.commit()
    user_menu.withdraw()
    main()
    sell_gui.destroy()
   
def scoreboard(self):
    import matplotlib.pyplot as plt
    import numpy as np

    # creating the dataset
    data = {'C':20, 'C++':15, 'Java':30,
            'Python':35}
    courses = list(data.keys())
    values = list(data.values())
      
    fig = plt.figure(figsize = (10, 5))
     
    # creating the bar plot
    plt.bar(courses, values, color ='black',
            width = 0.4)
     
    plt.xlabel("Student Username")
    plt.ylabel("Total value in £")
    plt.title("Students Portfolio Value")
    plt.show()
    
def exit(self):
    user_menu.destroy()
    messagebox.showinfo(title="Logged out", message="You have successfully logged out, have a nice day!")
    
    
    

create_account()



