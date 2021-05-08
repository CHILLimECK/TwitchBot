import ssl
import socket
import logging
import yaml

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s — %(message)s',
                    datefmt='%Y-%m-%d_%H:%M:%S',
                    handlers=[logging.FileHandler('meinbot.log', encoding='utf-8')])

with open("config.yml", "r") as config:
    cfg = yaml.load(config)

name = cfg["login"]["user"]
channel = '#'+cfg["login"]["channel"]
token = cfg["login"]["token"]
resp_teil1 = cfg["login"]["resp"]+' #'+str(name.lower() )+' '

tags = cfg["tags"]



def send(irc: ssl.SSLSocket, message: str):
    
    irc.send(bytes(f'{message}\r\n', 'UTF-8'))

def send_pong(irc: ssl.SSLSocket):
    send(irc, 'PONG :tmi.twitch.tv')

def handle(irc: ssl.SSLSocket, message: str):
    m = resp_teil1 +':'+ message
    print( "send: ",m)
    send(irc, m)

if __name__ == '__main__':
    

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    irc = context.wrap_socket(sock)

    irc.connect(('irc.chat.twitch.tv', 6697))

    send(irc, f'PASS oauth:{token}')
    send(irc, f'NICK {name}')
    send(irc, f'JOIN {channel}')

    try:
        while True:
            data = irc.recv(1024)
            raw_m = data.decode('UTF-8')

            for line in raw_m.splitlines():
                if line.startswith('PING :tmi.twitch.tv'):
                    send_pong(irc)
                else:
                    
                    comp = line.split()
                    message = comp[3:]
                    
                    if comp[1] == 'PRIVMSG':
                        user = line.split(':')[1].split('!')[0]
                        string = ' '.join(map(str, message))
                        string = string[1:]
                        
                        for tag in tags:
                            if tag in string.lower():
                                print("erwähnt von: ", user)
                                handle(irc, '/me ist derzeit leider afk')
                                break
                        logging.debug(user + " - " + string)
                    
        
    except KeyboardInterrupt:
        print("exit")
        sock.close()
        exit()

    

