#!/bin/env python

from bs4 import BeautifulSoup
import requests

import socket, ssl

class WikiBot:
    auth = False

    def __init__(self, host, port, nick, ident, realname):
        self.host = host
        self.port = port
        self.nick = nick
        self.ident = ident
        self.realname = realname
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.s=context.wrap_socket(socket.socket())

    def getHost(self):
        return self.host

    def getPort(self):
        return self.port

    def getNick(self):
        return self.nick

    def getIdent(self):
        return self.ident

    def getRealname(self):
        return self.realname

    def search(self, term):
        try:
            wcontent = requests.get("https://en.m.wikipedia.org/w/index.php?search=%s" % term).text
            soup = BeautifulSoup(wcontent).select("div > p")[0]
            return soup.get_text()
        except:
            return "Error not found"

    def send(self, data):
        self.s.send(data.encode())

    def join(self, channel):
        self.send("JOIN %s\r\n" % channel)

    def identify(self, password):
        self.send("PRIVMSG NICKSERV :IDENTIFY %s\r\n" % password)

    def connect(self):
        self.s.connect((self.host, self.port))
        self.send("NICK %s\r\n" % self.nick)
        self.send("USER %s %s * :%s\r\n" % (self.ident, self.host, self.realname))
        print("Connected to %s" % self.host)

    def run(self):
        readbuffer = ""
        while True:
            readbuffer=readbuffer+self.s.recv(1024).decode()
            temp=readbuffer.split("\n")
            readbuffer=temp.pop()

            for line in temp:
                line=line.rstrip().split()
                print(line)
                if(line[0]=="PING"):
                    self.send("PONG %s\r\n" % line[1])
                elif(len(line) > 3):
                    if(line[1]=="PRIVMSG"):
                        if(self.auth==False):
                            self.identify(str(input("Password: ")))
                            self.auth=True

                        if("#" in line[2] and ".wiki" in line[3]):
                            sterm = " ".join(line[4:])
                            self.send("PRIVMSG %s :%s\r\n" % (line[2], self.search(sterm)))
                        elif("#" in line[3]):
                            self.join(line[3].replace(":",""))
                    elif(line[1]=="INVITE"):
                        self.join(line[3].replace(":",""))


wbot = WikiBot("irc.rizon.net", 6697, "WikiBot", "WikiBot", "WikiBot")
wbot.connect()
wbot.run()
