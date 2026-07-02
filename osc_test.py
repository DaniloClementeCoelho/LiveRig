from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 8000)

print("enviando play")
client.send_message("/play", 1)
print("enviado")