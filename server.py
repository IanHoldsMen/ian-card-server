from http.server import BaseHTTPRequestHandler, HTTPServer
from http import cookies
from urllib.parse import parse_qs
import json
import sys

from card_db import CardDB
from session_store import SessionStore

gSessionStore = SessionStore()

class RequestHandler(BaseHTTPRequestHandler):

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)

    def handleCardsList(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        db = CardDB()
        cards = db.getAllCards()
        self.wfile.write(bytes(json.dumps(cards), "utf-8"))

    def handleCardsCreate(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("The text body:", body)
        parsed_body = parse_qs(body)
        print("The parsed body:", parsed_body)

        name = parsed_body["name"][0]
        suit = parsed_body["suit"][0]
        value = parsed_body["value"][0]
        db = CardDB()
        db.createCard(name, suit, value)

        self.send_response(201)
        self.end_headers()
    
    def handleCardsUpdate(self, id):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("The text body:", body)
        parsed_body = parse_qs(body)
        print("The parsed body:", parsed_body)
        
        db = CardDB()
        card = db.getCard(id)
        if card == None:
            self.handleNotFound()
            
        name = parsed_body["name"][0]
        suit = parsed_body["suit"][0]
        value = parsed_body["value"][0]
        
        db.updateCard(id, name, suit, value)

        self.send_response(200)
        self.end_headers()
    
    def handleCardsRetrieve(self, id):
        db = CardDB()
        card = db.getCard(id)

        if card == None:
            self.handleNotFound()
        else:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(card), "utf-8"))
    
    def handleCardsDelete(self, id):
        db = CardDB()
        card = db.getCard(id)
        
        if card == None:
            self.handleNotFound()
        else:
            db.deleteCard(id)
            self.send_response(200)
            self.end_headers()

    def handleNotFound(self):
        self.send_response(404)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Not found", "utf-8"))

       
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-type")
        self.end_headers()

    def do_DELETE(self):
        parts = self.path.split('/')[1:]
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            id = None
        
        if collection == "cards":
            if id == None:
                self.handleNotFound()
            else:
                self.handleCardsDelete(id)
        else:
            self.handleNotFound()

    def do_PUT(self):
        parts = self.path.split('/')[1:]
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            id = None
        
        if collection == "cards":
            if id == None:
                self.handleNotFound()
            else:
                self.handleCardsUpdate(id)
        else:
            self.handleNotFound()

    def do_GET(self):
        parts = self.path.split('/')[1:]
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            id = None
        
        if collection == "cards":
            if id == None:
                self.handleCardsList()
            else:
                self.handleCardsRetrieve(id)
        else:
            self.handleNotFound()

    
    def do_POST(self):
        if self.path == "/cards":
            self.handleCardsCreate()
        else:
            self.handleNotFound()
    
def run():

    db = CardDB()
    db.createCardTable()
    db = None

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, RequestHandler)

    print("Listening...")
    server.serve_forever()

run()