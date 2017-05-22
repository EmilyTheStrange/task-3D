#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler,HTTPServer
import cgi
import requests
import json
import time
from os import curdir, sep
import urllib

PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
    
    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        # Send upload form
        
        form = """
            <form id="uploadSTL" enctype="multipart/form-data" method="post" action="#">
            <input id="fileupload" name="STLfile" type="file" />
            <input type="submit" value="submit" id="submit" />
            </form>
            """
        self.wfile.write(bytes("Put your STL file\n" + form, "utf-8"))
        
        
    def do_POST(self):
        # http://stackoverflow.com/questions/13146064/simple-python-webserver-to-save-file
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type']})
                     
        filename = form['STLfile'].filename
        data = form['STLfile'].file.read()
        
        url_to_STL = myHandler.upload_to_3YOURMIND(data)
        
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        head = """
            <!doctype html>
            <html>
            <head>
                <title>Viewer</title>
                <style>
                    body {background-color: powderblue;}
                    h1 {color: red;}
                    p {color: blue;}
                  }
                </style>
             </head>
             <body>
            """
        res = """<iframe id="vs_iframe" align="center" src="https://www.viewstl.com/?embedded&url={}"
              style="border:10px;margin: 25%;width:50%;height:50%;"></iframe>""".format(url_to_STL)
        tail = """
            </body>
            </html>
             """
        
        # Doesn't do anything with posted data
        self.wfile.write(bytes(head + res + tail, "utf-8"))
        return
        
    def upload_to_3YOURMIND(myfile):
        showname = 'testingFile'
        url = 'https://api.3yourmind.com/v1/uploads/'
        files = {'file': (showname, myfile, 'application/sla')}
        fields = {"origin": "python_test"}

        response = requests.post(url,files=files,data=fields) # json
        response_json = json.loads(response.text)
        uuid = response_json["url"][34:-1]
        print(uuid)
        url_template = "https://3yourmind.s3.amazonaws.com/uploads/{}/repaired.stl".format(uuid)
        print(url_template)

        print(response.text)
        return url_template

try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print('Started httpserver on port ' , PORT_NUMBER)
    
    #Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()