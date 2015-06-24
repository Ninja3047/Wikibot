#!/bin/env python

import urllib.request
import urllib.parse
import json

import socket, ssl

import traceback

class WikiBot:
    wurl = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exchars=420&explaintext&redirects=&titles="

    def __init__(self, host, port, nick, ident, realname):
        self.host = host
        self.port = port
        self.nick = nick
        self.ident = ident
        self.realname = realname
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.s=context.wrap_socket(socket.socket())
        self.auth = False

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
            req = urllib.request.Request(self.wurl+urllib.parse.quote(term))
            req.add_header('User-Agent','WikiBot/2.0 ([email]) Simple IRC Bot')
            url = urllib.request.urlopen(req).read()
            content = json.loads(url.decode())['query']['pages']
            return next(iter(content.values()))['extract']
        except:
            print(traceback.format_exc())
            return "Not found"

    def sendraw(self, data):
        print(data)
        self.s.send(data.encode())

    def send(self, dest, data):
        data = data.replace("\n"," ")
        self.sendraw("PRIVMSG %s :%s\r\n" % (dest, data))

    def join(self, channel):
        self.sendraw("JOIN %s\r\n" % channel)

    def identify(self, password):
        self.sendraw("PRIVMSG NICKSERV :IDENTIFY %s\r\n" % password)

    def connect(self):
        self.s.connect((self.host, self.port))
        self.sendraw("NICK %s\r\n" % self.nick)
        self.sendraw("USER %s %s * :%s\r\n" % (self.ident, self.host, self.realname))
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
                    self.sendraw("PONG %s\r\n" % line[1])
                elif(len(line) > 3):
                    if(line[1]=="PRIVMSG"):
                        if(self.auth==False):
                            self.identify(str(input("Password: ")))
                            self.auth=True

                        if("#" in line[2] and ".wiki" in line[3]):
                            sterm = " ".join(line[4:])
                            print(sterm)
                            self.send(line[2], self.search(sterm))
                        elif("#" in line[3]):
                            self.join(line[3].replace(":",""))
                    elif(line[1]=="INVITE"):
                        self.join(line[3].replace(":",""))
