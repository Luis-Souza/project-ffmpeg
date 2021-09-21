from tkinter import *
import subprocess
import os
from tkinter import messagebox

class Application:
    PROCESS = None

    def __init__(self, master):
        self.master=master
        my_font=('roboto', 10, 'bold')
        #criando uma barra de menus
        barraDeMenu=Menu(self.master)
        menuFile=Menu(barraDeMenu,tearoff=0)
        menuFile.add_command(label="Limpar", command=self.clean)
        menuFile.add_separator()
        menuFile.add_command(label="Sair", command=lambda:self.close())
        barraDeMenu.add_cascade(label="File", menu=menuFile)

        barraDeMenu.add_command(label="sobre", command=self.sobre)

        self.master.config(menu=barraDeMenu)

        #definindo opção de dispositivos de entrada
        deviceOutput=Frame(self.master)
        deviceOutput.pack(pady=60)

        self.listDevices = list()
        for el in self.getaudiodevices():
            self.listDevices.append(self.getaudiodevices()[el])

        self.selectOutput = StringVar(deviceOutput)
        self.selectOutput.set(self.listDevices[0])
        Label(deviceOutput, text="Escolha o Dispositivo de entrada:").pack(side=LEFT)
        menuOutput = OptionMenu(deviceOutput, self.selectOutput, *self.listDevices)
        menuOutput.pack(side=RIGHT)

        #definindo endereço de transmição
        self.conecLb = Label(self.master, text="Desconectado", background="red", fg="white", font=my_font)        
        self.conecLb.place(x=30,y=145)
        Label(self.master, text="Transmission").place(x=30,y=170)
        self.transmission=Frame(self.master,borderwidth=1,relief="solid")
        self.transmission.place(x=30,y=190,width=240,height=100)

        Label(self.transmission,text="Address",pady=10).grid(row=1,column=1)
        self.address=Entry(self.transmission,width=20)
        self.address.grid(row=1,column=2)

        Label(self.transmission,text="Port",pady=10).grid(row=2,column=1)
        self.port=Entry(self.transmission,width=20)
        self.port.grid(row=2,column=2)

        #definindo opções de streaming
        Label(self.master,text="Streaming").place(x=280,y=170)
        self.streaming=Frame(self.master,borderwidth=1,relief="solid")
        self.streaming.place(x=280,y=190,width=200,height=100)

        self.listCodec = ["mp3","mp4"]
        self.listBitrate = ["64k","128k", "192k"]

        self.selectCodec = StringVar(self.streaming)
        self.selectCodec.set(self.listCodec[0])
        Label(self.streaming,text="Codec", pady="15").grid(row=1,column=1)
        menuCodec = OptionMenu(self.streaming, self.selectCodec, *self.listCodec)
        menuCodec.grid(row=1, column=2)

        self.selectBitrate = StringVar(self.streaming)
        self.selectBitrate.set(self.listBitrate[0])
        Label(self.streaming,text="Bitrate").grid(row=2,column=1)
        menuBitrate = OptionMenu(self.streaming, self.selectBitrate, *self.listBitrate)
        menuBitrate.grid(row=2, column=2)

        #botão para realizar a ação de streaming
        stop = Button(self.master, text="Parar", width="100")
        stop["command"] = self.stop
        stop.pack(side=BOTTOM)
        start = Button(self.master, text="Iniciar", width="100")
        start["command"] = self.send
        start.pack(side=BOTTOM, pady=5)

    def sobre(self):
        messagebox.showinfo(title="Sobre", message="Criado em 2021 por:jorge luis, marcos filho, vinicius fontineli, francisco carvalho")

    def updateConect(self,text):
        if(text=="Desconectado"):
            self.conecLb["text"] = "Desconectado"
            self.conecLb["background"] = "red"
        else:
            self.conecLb["text"] = "Conectado"
            self.conecLb["background"] = "green"

    def close(self):
        self.master.quit()
        if(self.PROCESS != None):
            args = ["kill",str(self.PROCESS.pid)]
            subprocess.run(args)
            self.PROCESS.kill()     
            self.updateConect("Desconectado")

    def clean(self):
        self.selectOutput.set(self.listDevices[0])
        self.selectCodec.set(self.listCodec[0])
        self.selectBitrate.set(self.listBitrate[0])
        self.address.delete(0,END)
        self.port.delete(0,END)

    def send(self):
        ip = self.addressGet()
        saida = self.cardGet()
        size = self.bitrateSize()
        porta = self.portGet()
        tipo = self.codecType()
        args = ["ffmpeg","-vn" ,"-f" ,"alsa", "-i", "sysdefault:"+saida, "-ac" ,"2" ,"-acodec", tipo, "-b:a" ,size ,"-f", "rtp",
                "rtp://"+ip+":"+ porta]
        self.PROCESS = subprocess.Popen(args)        
        if(self.PROCESS.pid):
            self.updateConect("Conectado")
    
    def stop(self):
        if(self.PROCESS.pid != None):
            args = ["kill",str(self.PROCESS.pid)]
            self.PROCESS.kill()     
            subprocess.run(args)
            self.updateConect("Desconectado")

    def cardGet(self):
        for el in self.getaudiodevices():
            if(self.getaudiodevices()[el] == self.selectOutput.get()):
                return el

    def addressGet(self):
        if(self.address.get() == ""):
            messagebox.showerror(title="Ip Address Error", message="Erro no endereço IP!")
            return;
        else:
            return self.address.get()

    def portGet(self):
        if(self.port.get() == ""):
            messagebox.showerror(title="PORT Error", message="Erro na PORTA!")
            return;
        else:
            return self.port.get()

    def codecType(self):    
        if(self.selectCodec.get() == "mp3"):
            return "libmp3lame"
        elif(self.selectCodec.get() == "mp4"):
            return ""

    def bitrateSize(self):
        if(self.selectBitrate.get() == "64k"):
            return "64k"
        elif(self.selectBitrate.get() == "128k"):
            return "128k"
        elif(self.selectBitrate.get() == "192k"):    
            return "192k"

    def findString(self,line, begin, end):
        name = ""
        for i in range(len(line)):
            if(i > begin and i < end):
                name += line[i]
        return name

    def getaudiodevices(self):
        nameDevices = {}
        devices = os.popen("arecord -l")
        device_string = devices.read()
        device_string = device_string.split("\n")
        for line in device_string:
            if(line.find("card") != -1):
                beginId = line.find(":")
                endId = line.find("[")
                beginDeviceFullName = line.find("device")+8
                endDeviceFullName = len(line)
                nameDevices[self.findString(line,beginId,endId).strip()] = self.findString(line,beginDeviceFullName,endDeviceFullName)                         
        return nameDevices

app = Tk()
app.title("Transmission Audio")
app.geometry("530x400")
Application(app)
app.mainloop()
