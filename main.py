# This is a sample Python script.
import os
import signal
import sys

import Ice

import getIP
from whisperer import Whisperer

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
Ice.loadSlice('./STT.ice')
import whisperIced


class SpeechReceiverI(whisperIced.SpeechReceiver):

    def __init__(self, serverTemplate):
        self.upload_data = None
        self.upload_completion = None
        self.communicator = serverTemplate.communicator
        self.template = None

        # Creating a media player
        self.whisperer = Whisperer()

    def addClient(self, adress, port, current):
        self.template = ClientTemplate(adress, port, self.communicator)


    def prepareUpload(self, nb_blocs: int, current):
        print("preparing download")
        self.upload_completion = []
        self.upload_data = []
        for index in range(0, nb_blocs):
            self.upload_completion.append(False)
        print("download prepared " + str(nb_blocs) + " blocs")


    def upload(self, bloc_id: int, data: bytes, current):
        self.upload_data.append(data)
        self.upload_completion[bloc_id] = True
        self.template.textSender.responseGetCompletion(self.upload_completion.count(True))

        if all(self.upload_completion):
            # Concaténez toutes les données pour reconstruire le fichier complet
            full_data = b"".join(self.upload_data)

            # Déterminez le chemin où enregistrer le fichier
            # Par exemple, enregistrez-le dans un dossier spécifique avec le nom spécifié
            save_path = "./recording.mp3"

            print("saving on : " + save_path)

            # Vérifiez si le dossier existe, sinon créez-le
            if not os.path.exists(os.path.dirname(save_path)):
                os.makedirs(os.path.dirname(save_path))

            # Enregistrez les données dans un nouveau fichier
            with open(save_path, "wb") as file:
                file.write(full_data)

            self.resetUpload()

            self.template.textSender.getTranscription(self.whisperer.transcribe(save_path))

    def resetUpload(self):
        # Réinitialisez toutes les variables d'upload pour une nouvelle transaction
        self.upload_data = [None] * len(self.upload_completion)
        self.upload_completion = [False] * len(self.upload_completion)

class ClientTemplate:
    port = "5000"
    adress = "localhost"

    def __init__(self, adress, port, communicator):
        proxy = communicator.stringToProxy("textSender:default -h " + adress + " -p " + port)
        self.textSender = whisperIced.TextSenderPrx.checkedCast(proxy)
        print("connected")

class ServerTemplate:

    port = "10000"
    adress = "localhost"

    def __init__(self, adress = "localhost", port = "10000"):
        self.communicator = Ice.initialize(sys.argv)
        self.adress = adress
        self.port = port

    def start(self):
        adapter = self.communicator.createObjectAdapterWithEndpoints("SpeechReceiver", "default -h " + self.adress + " -p " + self.port)
        adapter.add(SpeechReceiverI(self), Ice.stringToIdentity("speechReceiver"))
        adapter.activate()
        print("server UP")

    def listen(self, ):
        #
        # Ice.initialize returns an initialized Ice communicator,
        # the communicator is destroyed once it goes out of scope.
        #
            signal.signal(signal.SIGINT, lambda signum, frame: self.communicator.shutdown())
            if hasattr(signal, 'SIGBREAK'):
                signal.signal(signal.SIGBREAK, lambda signum, frame: self.communicator.shutdown())
            self.start()
            self.communicator.waitForShutdown()



if __name__ == '__main__':

    ip = getIP.get_ip()

    print("listening on : " + ip)

    myServer = ServerTemplate(ip, "6000")
    myServer.listen()

