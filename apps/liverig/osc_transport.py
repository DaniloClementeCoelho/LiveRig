from pythonosc.udp_client import SimpleUDPClient
import time

class OSCTransport:
    def __init__(self, host="127.0.0.1", port=8000):
        self.client = SimpleUDPClient(host, port)

    def play(self):
        self.client.send_message("/play", 1)

    def stop(self):
        self.client.send_message("/stop", 1)

    def pause(self):
        self.client.send_message("/pause", 1)

    def rewind(self):
        self.client.send_message("/rewind",1)
        time.sleep(0.05)
        self.client.send_message("/rewind",0)
        
    def goto_marker(self, marker: int):
        self.client.send_message("/marker", marker)
    
    def close_project(self):
        self.client.send_message("/closeproject", 1)