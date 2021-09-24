###PREPROCESING###
import os
from config import *
import tkinter as tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import tkcalendar as tkc
import time
import datetime
from sys import stderr
import pickle
import shutil
import logging as log
import zipnunzip as zp

###VARIABLES###
cosmetics=[]
carnets=[]
cosmeticLogs=[]
carnetLogs=[]


recError,recMessage=False,""
today=datetime.datetime.now()
dateFormat="%Y-%m-%d"
errFormat="%Y-%m-%d  %H:%M:%S"
backupFormat="%Y-%m-%d %H-%M"
thisMonthFormat="%Y-%m"

stdFont=(FONT_FAMILY,FONT_SIZE)

###CHANGE CURRENT DIRECTORY###
os.chdir(APP_PATH)

###PREPARE LOGS###
fhMain=log.FileHandler(LOGS_PATH)
fhPlt=log.FileHandler(PLOTS_LOGS_PATH)
log.basicConfig(filename=LOGS_PATH,encoding="utf-8",level=log.DEBUG)
logger=log.getLogger()

###FUNCTIONS###
def logWrite(state,msg):
    instant=datetime.datetime.now().strftime(errFormat)
    if state=="INFO":
        log.info("["+instant+"] "+msg)
    if state=="DEBUG":
        log.debug("["+instant+"] "+msg)
    if state=="ERROR":
        log.error("["+instant+"] "+msg)
    if state=="WARNING":
        log.warning("["+instant+"] "+msg)


def loadImage(source):
    return tk.PhotoImage(file=IMAGES_PATH+source)

def showCosmetics():
    for i in cosmetics:
        print(i)

def showCarnets():
    for i in carnets:
        print(i)

def clearLogs(logFile,maxsize):
    if os.path.getsize(logFile)>maxsize*1024**2:
        with open(logFile,"w") as log:
            log.truncate()

def swhoCosmeticLogs():
    for i in cosmeticLogs:
        print(i)

def showCarnetLogs():
    for i in carnetLogs:
        print(i)

def checkPaths():
    for i in [BACKUPS_PATH,BUFFERS_PATH,DB_PATH]:
        if not os.path.exists(i):
            os.mkdir(i)

def save(outfile,data,append=False):
    if append:
        with open(outfile,"wb+") as out:
            pickle.dump(data,out)
    else:
        with open(outfile,"wb") as out:
            pickle.dump(data,out)

def load(infile):
    with open(infile,"rb") as inp:
        return pickle.load(infile)

def setActive(window):
        window.lift()
        window.focus_force()
        window.grab_set()
        window.grab_release()

def normalizeName(name):
    length=len(name)
    if length==0:
        return ""
    i=0
    while ord(name[i])==32: 
        i+=1
        if i>=length:
            i-=1
            break
    name=name[i:]
    return name.upper()
        

###WINDOWS###
class Window():
    otherWindows={}
    it=0
    frames=[]
    actionStack=[]
    def __init__(self,cpt):
        self.master=tk.Tk()
        self.master.title(cpt)
        self.master.iconphoto(False,loadImage("ico.png"))
        self.master.geometry(str(WIDTH)+"x"+str(HEIGHT))
        self.master.protocol("WM_DELETE_WINDOW",self.on_clossing)
        logWrite("INFO","Session started. Program path: {}".format(os.getcwd()))


        ###PANELS###
        self.main=tk.PanedWindow(self.master,bd=BD_SIZE,bg=PANEL_COLOR,orient=tk.HORIZONTAL)
        self.lpanel=tk.PanedWindow(self.main,bd=BD_SIZE,bg=PANEL_COLOR,orient=tk.VERTICAL)
        self.rpanel=tk.PanedWindow(self.main,bd=BD_SIZE,bg=PANEL_COLOR,orient=tk.VERTICAL)

        self.menu=tk.PanedWindow(self.lpanel,bd=BD_SIZE,bg=PANEL_COLOR,relief="solid")
        self.table=tk.PanedWindow(self.lpanel,bd=BD_SIZE,bg=PANEL_COLOR,relief="solid")

        self.oper=tk.PanedWindow(self.rpanel,bd=BD_SIZE,bg=PANEL_COLOR,relief="solid")
        self.actPan=tk.PanedWindow(self.rpanel,bd=BD_SIZE,bg=PANEL_COLOR,relief="solid")

        self.main.pack(fill=tk.BOTH,expand=1)
        self.main.add(self.lpanel)
        self.main.add(self.rpanel)

        self.lpanel.add(self.menu)
        self.lpanel.add(self.table)

        self.rpanel.add(self.oper)
        self.rpanel.add(self.actPan)

        ###BINDING###
        self.master.bind("<Escape>",self.on_clossing)


    def panel(self,panel):
        if not panel:
            return self.menu
        else:
            return self.table

    def run(self):
        self.master.after(2000,self.search4Collisions())
        self.master.mainloop()

    def rememberFrame(self,frame):
        Window.frames.append(frame)

    def addFrame(self,which,newFrame,oldFrame=None):
        if which==0:
            if oldFrame:
                self.menu.forget(oldFrame)
            self.menu.add(newFrame,width=640)
        elif which==1:
            if oldFrame:
                self.table.forget(oldFrame)
            self.table.add(newFrame)
        elif which==2:
            if oldFrame:
                self.oper.forget(oldFrame)
            self.oper.add(newFrame,height=600)
        elif which==3:
            if oldFrame:
                self.actPan.forget(oldFrame)
            self.actPan.add(newFrame)
        else:
            logWrite("ERROR","Packing frame to no existing Panned Window")
            return False

    def on_clossing(self,event=None):
        if tk.messagebox.askokcancel("Wyjście","Czy napewno chesz wyjść?\nWszystkie niezapisane zmiany zostaną utracone."):
            for child in self.master.winfo_children(): 
                child.destroy()
            
            for i in Window.otherWindows:
                try:
                    Window.otherWindows[i].destroy()
                except:
                    logWrite("ERROR","Windows has been already terminated")
            logWrite("INFO","Session finished.\n")
            self.master.destroy()

    def search4Collisions(self):
        global recError
        if recError:
            recError=False
            ErrorWindow("Uwaga","Wykryto niezgodność",recMessage).run()
        self.master.after(2000,self.search4Collisions)


class ErrorWindow():
    def __init__(self,caption,header,text):
        self.root=tk.Tk()
        self.root.title(caption)
        self.root.geometry(str(ERR_WIDTH)+"x"+str(ERR_HEIGHT))
        self.root.grid_rowconfigure(0,weight=1)
        self.root.grid_columnconfigure(0,weight=1)
        setActive(self.root)
        
        Window.otherWindows[Window.it]=self.root
        Window.it+=1

        self.fr=tk.Frame(self.root,bg=BG_COLOR)
        self.fr.pack(fill=tk.BOTH,expand=1)

        self.header=tk.Label(self.fr,text=header,bg=BG_COLOR,fg=FONT_COLOR)
        self.message=tk.Label(self.fr,font=stdFont,text=text,bg=BG_COLOR,fg=FONT_COLOR,wraplength=400,justify=tk.LEFT)
        self.header.grid(row=0,column=0,sticky=tk.EW)
        self.message.grid(row=1,column=0,sticky=tk.EW)

        self.agrBn=tk.Button(self.fr,text="Ok",command=self.do,bg=BG_COLOR,fg=FONT_COLOR)
        self.agrBn.grid(row=2,column=0,sticky=tk.EW)

        self.root.bind("<Return>",self.do)

    def run(self):
        self.root.mainloop()

    def do(self,event=None):
        self.root.destroy()

class StatisticsWindow():
    def __init__(self):
        self.root=tk.Tk()
        self.root.title("Statystyki")
        self.root.geometry(SLV_WIDTH+"x"+SLV_HEIGHT)
        setActive(self.root)
        
        Window.otherWindows[Window.it]=self.root
        self.winId=Window.it
        Window.it+=1

        plt.style.use("fivethirtyeight")
        self.fig=Figure(dpi=100)
        self.ax=self.fig.add_subplot(111)
        self.canv=FigureCanvasTkAgg(self.fig,master=self.root)
        self.draw()
        ###BINDING###
        self.root.bind("<Return>",self.do)

    def draw(self):
        names=[i.nameVar.get() for i in CosmTable.rows]
        vals=[int(i.thisMntVar.get()) for i in CosmTable.rows]
        

        self.ax.bar(names,vals)
        self.ax.set_title("Bilans kosmetyków na "+today.strftime(thisMonthFormat))
        self.ax.set_xlabel("Kosmetyk")
        self.ax.set_ylabel("Stan")
        labels=self.ax.get_xticklabels()
        plt.setp(labels,rotation=45,horizontalalignment="right")


        self.canv.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
    def run(self):
        self.root.mainloop()
    
    def do(self,event=None):
        del Window.otherWindows[self.winId]
        self.root.destroy()
        del self

        

class BackupManager():
    def __init__(self):
        self.root=tk.Tk()
        self.root.geometry(SMALL_WIN_WIDTH+"x"+SMALL_WIN_HEIGHT)
        self.root.title("Kopie bezpieczeństwa")
        setActive(self.root)

        Window.otherWindows[Window.it]=self.root
        self.winId=Window.it
        Window.it+=1

        self.fr=tk.Frame(self.root,bg=BG_COLOR,height=100,width=400)
        self.fr.pack(fill=tk.BOTH)
        self.buffPath=os.getcwd()


        ###BUTTONS###
        self.newBn=tk.Button(self.fr,font=stdFont,text="Utwórz\nkopię zapasową",fg=FONT_COLOR,bg=BG_COLOR,command=self.newBackup,width=15)
        self.loadBn=tk.Button(self.fr,font=stdFont,text="Wczytaj\nkopię zapasową",fg=FONT_COLOR,bg=BG_COLOR,command=self.loadBackup,width=15)
        
        ###CANVAS###
        self.canv=tk.Canvas(self.root,bg=BG_COLOR,bd=BD_SIZE)
        self.canv.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)

        ###SCROLLBAR###
        self.sb=ttk.Scrollbar(self.root,orient=tk.VERTICAL,command=self.canv.yview)
        self.sb.pack(side=tk.RIGHT,fill=tk.Y)

        self.canv.configure(yscrollcommand=self.sb.set)
        self.canv.bind("<Configure>", lambda e:self.canv.configure(scrollregion=self.canv.bbox("all")))

        ###LISTBOX###
        self.bplist=tk.Listbox(self.canv,bg=BG_COLOR,bd=BD_SIZE,fg=FONT_COLOR,width=47,font=stdFont,height=14)
        bps=[f for root,dirs,f in os.walk(BACKUPS_PATH)]
        for i in bps[0]:
            self.bplist.insert(tk.END,i)
        

        self.canv.create_window((0,0),window=self.bplist,anchor="nw")
        
        ###PACKING###
        self.newBn.grid(row=0,column=1)
        self.loadBn.grid(row=0,column=2)
        self.fr.grid_columnconfigure(0,minsize=55)
        self.fr.grid_columnconfigure(3,minsize=55)
        

        ###BINDING###
        self.root.bind("<Escape>",self.do)

    def loadBackup(self):
        os.chdir(DB_PATH)
        try:
            zp.extract(self.buffPath+"/backup/"+self.bplist.get(tk.ACTIVE),APP_PATH)
        except:
            logWrite("ERROR","No positon selected or problem with file.")
            ErrorWindow("Błąd","Nie udało się wczytać kopii.","Proces przerwany niepowodzeniem.").run()
            return
        for i in ["cosm.txt","cosmLog.txt","carn.txt","carnLog.txt"]:
            if os.path.exists(i):
                os.remove(i)
        zp.extract(self.buffPath+"/backup/"+self.bplist.get(tk.ACTIVE),DB_PATH)
        os.chdir(APP_PATH)
        ErrorWindow("Kopia zapasowa wczytana","Wczytano kopię.","Kopia zapasowa została wczytana pomyślnie. Proszę o ponowne uruchomienie programu.").run()

        
    def newBackup(self):
        os.chdir(DB_PATH)
        zp.archive(self.buffPath+"/backup/Backup_"+datetime.datetime.now().strftime(backupFormat),"cosm.txt","carn.txt","carnLog.txt","cosmLog.txt")
        os.chdir("..")
        ErrorWindow("Nowa kopia zapasowa","Dodano kopię.","Nowa kopia zapasowa została dodana pomyślnie i będzie dostępna po ponownym uruchomieniu programu.").run()

    def run(self):
        self.root.mainloop()
    
    def do(self,event=None):
        del Window.otherWindows[self.winId]
        self.root.destroy()



###FRAMES###
class Menu(tk.Frame):
    def __init__(self,master,win):
        super().__init__(master.master,bg=BG_COLOR,bd=BD_SIZE,relief="solid",height=100)
        
        self.win=win
        self.view=tk.StringVar(self)
        self.view.set("Karnety")

        ###MAIN:BUTTONS###
        self.history=tk.Button(self,font=stdFont,text="Kopia\nbezpieczeństwa",bg=BUTTON_COLOR,fg=FONT_COLOR,command=lambda: self.open(0),width=BUTTON_WIDTH,height=BUTTON_HEIGHT)
        self.vip=tk.Button(self,font=stdFont,textvariable=self.view,bg=BUTTON_COLOR,fg=FONT_COLOR,command=lambda: self.open(1),width=BUTTON_WIDTH,height=BUTTON_HEIGHT)
        self.draw=tk.Button(self,font=stdFont,text="Statystyki",bg=BUTTON_COLOR,fg=FONT_COLOR,command=lambda:self.open(2),width=BUTTON_WIDTH,height=BUTTON_HEIGHT)
        self.save=tk.Button(self,font=stdFont,text="Zapisz",bg=BUTTON_COLOR,fg=FONT_COLOR,command=lambda:self.open(3),width=BUTTON_WIDTH,height=BUTTON_HEIGHT)

        ###PACKING###
        self.history.grid(row=0,column=0)
        self.vip.grid(row=0,column=1)
        self.draw.grid(row=0,column=2)
        self.save.grid(row=0,column=3)
        for i in range(4):
            self.grid_columnconfigure(i,minsize=159)


    def open(self,val):
        if val==0:
            BackupManager().run()
        elif val==1:
            j=1
            if self.view.get()=="Karnety":
                self.view.set("Kosmetyki")
                for i in range(0,5,2):
                    self.win.addFrame(j,Window.frames[i+1],Window.frames[i])
                    j+=1

            else:
                self.view.set("Karnety")

                for i in range(0,5,2):
                    self.win.addFrame(j,Window.frames[i],Window.frames[i+1])
                    j+=1

        elif val==2:
            for hdlr in logger.handlers[:]:
                logger.removeHandler(hdlr)
            logger.addHandler(fhPlt)
            StatisticsWindow().run()
            for hdlr in logger.handlers[:]:
                logger.removeHandler(hdlr)
            logger.addHandler(fhMain)

        elif val==3:
            for child in Window.frames:
                #print(type(child),type)
                if  (type(child) is CosmTable) or (type(child) is CosmLogTable) or (type(child) is CarnTable) or (type(child) is CarnLogTable): 
                    child.save()



class CosmTable(tk.Frame):
    iter=0
    rows=[]
    def __init__(self,master):
        super().__init__(master.master,bg=BG_COLOR,bd=BD_SIZE)

        ###CANVAS###
        self.canv=tk.Canvas(self,bg=BG_COLOR,bd=BD_SIZE)
        self.canv.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)

        ###SCROLLBAR###
        self.sb=ttk.Scrollbar(self,orient=tk.VERTICAL,command=self.canv.yview)
        self.sb.pack(side=tk.RIGHT,fill=tk.Y)

        self.canv.configure(yscrollcommand=self.sb.set)
        self.canv.bind("<Configure>", lambda e:self.canv.configure(scrollregion=self.canv.bbox("all")))

        self.inner=tk.Frame(self.canv,bg=BG_COLOR,bd=BD_SIZE)

        self.canv.create_window((0,0),window=self.inner,anchor="nw")

        ###ADD HEADERS###
        idLbl=tk.Label(self.inner,font=stdFont,text="ID",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=5)
        nameLbl=tk.Label(self.inner,font=stdFont,text="KOSMETYK",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=20)
        amntLbl=tk.Label(self.inner,font=stdFont,text="ILOŚĆ",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=6)
        weekLbl=tk.Label(self.inner,font=stdFont,text="BILANS MIESIĘCZNY",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=17)
        dateLbl=tk.Label(self.inner,font=stdFont,text="OSTATNIA OPERACJA",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=18)

        idLbl.grid(row=0,column=0,sticky=tk.EW)
        nameLbl.grid(row=0,column=1,sticky=tk.EW)
        amntLbl.grid(row=0,column=2,sticky=tk.EW)
        weekLbl.grid(row=0,column=3,sticky=tk.EW)
        dateLbl.grid(row=0,column=4,sticky=tk.EW)
        
        CosmTable.iter+=1

    def load(self):
        logWrite("INFO","Loading cosmetics...")
        if os.path.isfile(COSM_PATH):
            try:
                with open(COSM_PATH) as out:
                    buff=out.read().split(";")
                    for i in buff[:-1]:
                        cosm=i.split("^")
                        self.add(CosmRow(self.inner,Cosmetic(cosm[0],int(cosm[1])),cosm[2]))
                logWrite("INFO","cosm.txt loaded successfully.")

            except:
                logWrite("WARNING","cosm.txt is broken. Loading denied! To regain your data use backup file!\n")
                global recError
                global recMessage
                recError,recMessage=True,"Błąd wczytywania bazy danych kosmetyków."



    def add(self,cR):
        ###PACKING###
        cR.idLbl.grid(row=CosmTable.iter,column=0,sticky=tk.EW)
        cR.name.grid(row=CosmTable.iter,column=1,sticky=tk.EW)
        cR.amn.grid(row=CosmTable.iter,column=2,sticky=tk.EW)
        cR.thisMntLbl.grid(row=CosmTable.iter,column=3,sticky=tk.EW)
        cR.lstUpdLbl.grid(row=CosmTable.iter,column=4,sticky=tk.EW)
        
        CosmTable.iter+=1
        CosmTable.rows.append(cR)
        
        ###MOVE SCROLLBAR###
        self.canv.configure(scrollregion=self.canv.bbox("all"))
        self.canv.yview("moveto",0.9)

    def save(self):
        with open(BUFFERS_PATH+"cosmBuffer.txt","w") as out:
            out.truncate()
        try:
            with open(BUFFERS_PATH+"cosmBuffer.txt","a") as out:
                for i in CosmTable.rows:
                    buffer=i.nameVar.get()+"^"+str(i.amnVar.get())+"^"+i.lastUpdateVal.get()+";"
                    out.write(buffer)
            shutil.copyfile(BUFFERS_PATH+"cosmBuffer.txt",COSM_PATH)
            logWrite("INFO","Changes in cosmetics saved.")
        except:
            logWrite("WARNING","Wrong rows format. Save to cosmBuffer.txt denied!")
            global recError
            global recMessage
            recError,recMessage=True,"Błąd zapisu bazy danych kosmetyków."
            return
        


class ActionMenu(tk.Frame):
    def __init__(self,master,cTable,logTable,crTable,crlTable):
        super().__init__(master.master,bg=BG_COLOR,bd=BD_SIZE)
        
        ###MASTERS###
        self.cosmTable=cTable
        self.logcosmTable=logTable
        self.carnTable=crTable
        self.logcarnTable=crlTable

        ###BUTTONS###
        self.updBn=tk.Button(self,text="Uaktualnij",font=stdFont,command=self.update,bg=BG_COLOR,fg=FONT_COLOR,width=BUTTON_WIDTH,height=BUTTON_HEIGHT)
        self.addBn=tk.Button(self,text="Dodaj kosmetyk",font=stdFont,command=self.add,bg=BG_COLOR,fg=FONT_COLOR,width=BUTTON_WIDTH,height=BUTTON_HEIGHT)
        self.undBn=tk.Button(self,text="Cofnij",font=stdFont,command=self.undo,bg=BG_COLOR,fg=FONT_COLOR,width=BUTTON_WIDTH,height=BUTTON_HEIGHT)

        

        ###PACKING###
        self.updBn.grid(row=0,column=0,padx=220,pady=3)
        self.addBn.grid(row=1,column=0,pady=3)
        self.undBn.grid(row=2,column=0,pady=3)

    def update(self):
        if cosmetics==[]:
            logWrite("WARNING","Cosmetics list is empty!")
            global recError
            global recMessage
            recError,recMessage=True,"Lista kosmetyków jest pusta."
            return
        ###LOGS###
        logWrite("DEBUG","Update cosmetic action detected.")

        buff=UpdateCosm(self.cosmTable,self.logcosmTable)
        buff.run()
        logWrite("DEBUG","Update cosmetic window is active.")   

    def add(self):
        ###LOGS###
        logWrite("DEBUG","Add cosmetic action detected.")

        buff=AddCosm(self.cosmTable,self.logcosmTable)        
        buff.run()
        
        logWrite("DEBUG","Add cosmetic window is active.")

    def undo(self):
        ###LOGS###
        logWrite("DEBUG","Undo action detected.")
        if len(Window.actionStack)==0:
            logWrite("DEBUG","Undo denied. Stack is empty.")
        else:
            action=Window.actionStack.pop()
            if action["Action"]=="Add":
                ###REMOVE ADDED OBJECT###
                if action["Object"]=="Cosmetic":
                    cosmetics.pop()
                    Cosmetic.id-=1
                    cosmeticLogs.pop()
                    CosmeticLog.id-=1
                    ob=CosmTable.rows.pop()
                    ob.clear()
                    CosmTable.iter-=1
                    ob=CosmLogTable.rows.pop()
                    ob.clear()
                    CosmLogTable.iter-=1
                else:
                    carnets.pop()
                    carnetLogs.pop()
                    ob=CarnTable.rows.pop()
                    ob.clear()
                    CarnTable.iter-=1
                    ob=CarnLogTable.rows.pop()
                    ob.clear()
                    CarnLogTable.iter-=1
            elif action["Action"]=="Update":
                ###UNDO UPDATE###
                if action["Object"]=="Cosmetic":
                    cosmeticLogs.pop()
                    CosmeticLog.id-=1
                    ob=CosmLogTable.rows.pop()
                    ob.clear()
                    CosmLogTable.iter-=1
                    for i in cosmetics:
                        if action["ItemId"]==i.id:
                            i.update(action["Ammount"]*-1)
                    for i in CosmTable.rows:
                        if action["ItemId"]==i.id:
                            i.update()
                    Window.actionStack.pop()

                else:
                    carnetLogs.pop()
                    CarnetLog.id-=1
                    ob=CarnLogTable.rows.pop()
                    ob.clear()
                    CarnLogTable.iter-=1
                    for i in carnets:
                        if action["ItemId"]==i.id:
                            i.update(action["Ammount"]*-1)
                    for i in CarnTable.rows:
                        if action["ItemId"]==i.id:
                            i.update()
                    Window.actionStack.pop()
            else:
                ###UNDO REMOVE CARNET OPERATION###
                carnetLogs.pop()
                CarnetLog.id-=1
                ob=CarnLogTable.rows.pop()
                ob.clear()
                CarnLogTable.iter-=1
                name,surename=action["Ammount"]["Person"].split(" ")
                total,minutes=action["Ammount"]["Total"],action["Ammount"]["Minutes"]
                self.carnTable.add(CarnRow(self.carnTable.inner,Carnet(action["ItemId"],name,surename,total,minutes)))
                Window.actionStack.pop()
            logWrite("DEBUG","Undo last operation.")




class CActionMenu(tk.Frame):
    def __init__(self,master,cTable,logTable):
        super().__init__(master.master,bg=BG_COLOR,bd=BD_SIZE)
        
        ###MASTERS###
        self.carnTable=cTable
        self.logcarnTable=logTable

        ###BUTTONS###
        self.updBn=tk.Button(self,font=stdFont,text="Uaktualnij",command=self.update,bg=BG_COLOR,fg=FONT_COLOR,width=BUTTON_WIDTH,height=BUTTON_HEIGHT)
        self.addBn=tk.Button(self,font=stdFont,text="Dodaj karnet",command=self.add,bg=BG_COLOR,fg=FONT_COLOR,width=BUTTON_WIDTH,height=BUTTON_HEIGHT)
        self.udBn=tk.Button(self,font=stdFont,text="Cofnij",command=self.undo,bg=BG_COLOR,fg=FONT_COLOR,width=BUTTON_WIDTH,height=BUTTON_HEIGHT)
        self.rmBn=tk.Button(self,font=stdFont,text="Usuń karnet",command=self.remove,bg=BG_COLOR,fg=FONT_COLOR,width=BUTTON_WIDTH,height=BUTTON_HEIGHT)


        ###PACKING###
        self.updBn.grid(row=0,column=0,padx=220,pady=3)
        self.addBn.grid(row=1,column=0,pady=3)
        self.udBn.grid(row=2,column=0,pady=3)
        self.rmBn.grid(row=3,column=0,pady=3)

    def update(self):
        if carnets==[]:
            logWrite("WARNING","Carnet list is empty!")
            global recError
            global recMessage
            recError,recMessage=True,"Lista karnetów jest pusta."
            return
        buff=UpdateCarn(self.carnTable,self.logcarnTable)
        buff.run()
    def add(self):
        buff=AddCarn(self.carnTable,self.logcarnTable)        
        buff.run()
    def undo(self):
        ###LOGS###
        logWrite("DEBUG","Undo action detected.")
        if len(Window.actionStack)==0:
            logWrite("DEBUG","Undo denied. Stack is empty.")
        else:
            action=Window.actionStack.pop()
            if action["Action"]=="Add":
                ###REMOVE ADDED OBJECT###
                if action["Object"]=="Cosmetic":
                    cosmetics.pop()
                    Cosmetic.id-=1
                    cosmeticLogs.pop()
                    CosmeticLog.id-=1
                    ob=CosmTable.rows.pop()
                    ob.clear()
                    CosmTable.iter-=1
                    ob=CosmLogTable.rows.pop()
                    ob.clear()
                    CosmLogTable.iter-=1
                else:
                    carnets.pop()
                    carnetLogs.pop()
                    ob=CarnTable.rows.pop()
                    ob.clear()
                    CarnTable.iter-=1
                    ob=CarnLogTable.rows.pop()
                    ob.clear()
                    CarnLogTable.iter-=1
            elif action["Action"]=="Update":
                ###UNDO UPDATE###
                if action["Object"]=="Cosmetic":
                    cosmeticLogs.pop()
                    CosmeticLog.id-=1
                    ob=CosmLogTable.rows.pop()
                    ob.clear()
                    CosmLogTable.iter-=1
                    for i in cosmetics:
                        if action["ItemId"]==i.id:
                            i.update(action["Ammount"]*-1)
                    for i in CosmTable.rows:
                        if action["ItemId"]==i.id:
                            i.update()
                    Window.actionStack.pop()
                    
                else:
                    carnetLogs.pop()
                    CarnetLog.id-=1
                    ob=CarnLogTable.rows.pop()
                    ob.clear()
                    CarnLogTable.iter-=1
                    for i in carnets:
                        if action["ItemId"]==i.id:
                            i.update(action["Ammount"]*-1)
                    for i in CarnTable.rows:
                        if action["ItemId"]==i.id:
                            i.update()
                    Window.actionStack.pop()
            else:
                ###UNDO REMOVE CARNET OPERATION###
                carnetLogs.pop()
                CarnetLog.id-=1
                ob=CarnLogTable.rows.pop()
                ob.clear()
                CarnLogTable.iter-=1
                name,surename=action["Ammount"]["Person"].split(" ")
                total,minutes=action["Ammount"]["Total"],action["Ammount"]["Minutes"]
                self.carnTable.add(CarnRow(self.carnTable.inner,Carnet(action["ItemId"],name,surename,total,minutes)))
                Window.actionStack.pop()
            logWrite("DEBUG","Undo last operation.")
    
    def remove(self):
        RemoveCarn(self.carnTable,self.logcarnTable).run()
      

class CosmLogTable(tk.Frame):
    iter=1
    rows=[]
    def __init__(self,master):
        super().__init__(master.master,bg=BG_COLOR,bd=BD_SIZE)

        ###CANVAS###
        self.canv=tk.Canvas(self,bg=BG_COLOR,bd=BD_SIZE)
        self.canv.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)

        ###SCROLLBAR###
        self.sb=ttk.Scrollbar(self,orient=tk.VERTICAL,command=self.canv.yview)
        self.sb.pack(side=tk.RIGHT,fill=tk.Y)

        self.canv.configure(yscrollcommand=self.sb.set)
        self.canv.bind("<Configure>", lambda e:self.canv.configure(scrollregion=self.canv.bbox("all")))

        self.inner=tk.Frame(self.canv,bg=BG_COLOR,bd=BD_SIZE)
        self.canv.configure(scrollregion=self.inner.bbox("all"))
        self.canv.create_window((0,0),window=self.inner,anchor="nw")

    
        ###ADD HEADERS###
        idLbl=tk.Label(self.inner,font=stdFont,text="ID",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=5)
        nameLbl=tk.Label(self.inner,font=stdFont,text="KOSMETYK",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=20)
        opLbl=tk.Label(self.inner,font=stdFont,text="OPERACJA",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=19)
        dateLbl=tk.Label(self.inner,font=stdFont,text="DATA OPERACJI",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=15)

        idLbl.grid(row=0,column=0,sticky=tk.EW)
        nameLbl.grid(row=0,column=1,sticky=tk.EW)
        opLbl.grid(row=0,column=2,sticky=tk.EW)
        dateLbl.grid(row=0,column=3,sticky=tk.EW)

    def add(self,row):
        ###PACKING###
        row.idLbl.grid(row=CosmLogTable.iter,column=0,sticky=tk.EW)
        row.name.grid(row=CosmLogTable.iter,column=1,sticky=tk.EW)
        row.amn.grid(row=CosmLogTable.iter,column=2,sticky=tk.EW)
        row.dateLbl.grid(row=CosmLogTable.iter,column=3,sticky=tk.EW)
        
        CosmLogTable.iter+=1
        CosmLogTable.rows.append(row)
        ###MOVE SCROLLBAR###
        self.canv.configure(scrollregion=self.canv.bbox("all"))
        self.canv.yview("moveto",0.9)
    
    def load(self):
        logWrite("INFO","Loading cosmetic logs...")
        if os.path.isfile(COSML_PATH):
            try:
                with open(COSML_PATH) as out:
                    buff=out.read().split(";")
                    for i in buff[:-1]:
                        cosmLog=i.split("^")
                        self.add(CosmLogRow(self.inner,CosmeticLog(cosmLog[0],int(cosmLog[1]),cosmLog[2])))
                logWrite("INFO","cosmLog.txt loaded successfully.")
                
            except:
                logWrite("WARNING","cosmLog.txt is broken. Loading denied! To regain your data use backup file!\n")
                global recError
                global recMessage
                recError,recMessage=True,"Błąd wczytywania bazy danych operacji kosmetyków."


    def save(self):
        with open(BUFFERS_PATH+"cosmLogBuffer.txt","w") as out:
            out.truncate()
        try:
            with open(BUFFERS_PATH+"cosmLogBuffer.txt","a") as out:
                for i in CosmLogTable.rows:
                    buffer=i.nameVar.get()+"^"+str(i.value)+"^"+i.dateVal.get()+";"
                    out.write(buffer)
            shutil.copy(BUFFERS_PATH+"cosmLogBuffer.txt",COSML_PATH)
            logWrite("INFO","Changes in cosmetic're logs saved.")
        except:
            logWrite("WARNING","Wrong rows format. Save denied!\n")
            global recError
            global recMessage
            recError,recMessage=True,"Błąd zapisu bazy danych operacji kosmetyków."
            return


class CarnTable(tk.Frame):
    rows=[]
    iter=1

    def __init__(self,master):
        super().__init__(master.master,bg=BG_COLOR,bd=BD_SIZE)

        ###CANVAS###
        self.canv=tk.Canvas(self,bg=BG_COLOR,bd=BD_SIZE)
        self.canv.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)

        ###SCROLLBAR###
        self.sb=ttk.Scrollbar(self,orient=tk.VERTICAL,command=self.canv.yview)
        self.sb.pack(side=tk.RIGHT,fill=tk.Y)

        self.canv.configure(yscrollcommand=self.sb.set)
        self.canv.bind("<Configure>", lambda e:self.canv.configure(scrollregion=self.canv.bbox("all")))

        self.inner=tk.Frame(self.canv,bg=BG_COLOR,bd=BD_SIZE)

        self.canv.create_window((0,0),window=self.inner,anchor="nw")

        ###ADD HEADERS###
        idLbl=tk.Label(self.inner,text="ID",bg=BG_COLOR,fg=FONT_COLOR,font=stdFont,bd=BD_SIZE,relief="solid",width=6)
        prsnLbl=tk.Label(self.inner,text="WŁAŚCICIEL",bg=BG_COLOR,fg=FONT_COLOR,font=stdFont,bd=BD_SIZE,relief="solid",width=29)
        usertimeLbl=tk.Label(self.inner,text=" BILANS CZASU",bg=BG_COLOR,fg=FONT_COLOR,font=stdFont,bd=BD_SIZE,relief="solid",width=13)
        lstUpdLbl=tk.Label(self.inner,text="OSTATNIA OPERACJA",bg=BG_COLOR,fg=FONT_COLOR,font=stdFont,bd=BD_SIZE,relief="solid",width=18)
        
        idLbl.grid(row=0,column=0,sticky=tk.EW)
        prsnLbl.grid(row=0,column=1,sticky=tk.EW)
        usertimeLbl.grid(row=0,column=2,sticky=tk.EW)
        lstUpdLbl.grid(row=0,column=3,sticky=tk.EW)

    def load(self):
        logWrite("INFO","Loading carnets...")
        if os.path.isfile(CARN_PATH):
            try:
                with open(CARN_PATH) as out:
                    buff=out.read().split(";")
                    for i in buff[:-1]:
                        carn=i.split("^")
                        name,sname=carn[1].split(" ")

                        ###CHECK IF ID IS CORRECT###
                        int(carn[0])
                        self.add(CarnRow(self.inner,Carnet(carn[0],name,sname,carn[2],int(carn[3])),carn[4]))
                logWrite("INFO","carn.txt loaded successfully.")
                

            except:
                logWrite("WARNING","carn.txt is broken. Loading denied! To regain your data use backup file!\n")
                global recError
                global recMessage
                recError,recMessage=True,"Błąd wczytywania bazy danych karnetów."



    def add(self,row):
        row.idLbl.grid(row=CarnTable.iter,column=0,sticky=tk.EW)
        row.prsnLbl.grid(row=CarnTable.iter,column=1,sticky=tk.EW)
        row.usertimeLbl.grid(row=CarnTable.iter,column=2,sticky=tk.EW)
        row.lstUpdLbl.grid(row=CarnTable.iter,column=3,sticky=tk.EW)
       
        CarnTable.iter+=1
        CarnTable.rows.append(row)

        ###MOVE SCROLLBAR###
        self.canv.configure(scrollregion=self.canv.bbox("all"))
        self.canv.yview("moveto",0.9)

    def save(self):
        with open(BUFFERS_PATH+"carnBuffer.txt","w") as out:
            out.truncate()
        try:
            with open(BUFFERS_PATH+"carnBuffer.txt","a") as out:
                for i in CarnTable.rows:
                    buffer=i.id+"^"+i.person+"^"+str(i.total)+"^"+str(i.minutesVar.get())+"^"+i.lastUpdateVal.get()+";"
                    out.write(buffer)
            shutil.copyfile(BUFFERS_PATH+"carnBuffer.txt",CARN_PATH)
            logWrite("INFO","Changes in carnets saved.")
        except:
            logWrite("WARNING","Wrong rows format. Save denied!")
            global recError
            global recMessage
            recError,recMessage=True,"Błąd zapisu bazy danych karnetów."
            return
        

class CarnLogTable(tk.Frame):
    iter=1
    rows=[]
    def __init__(self,master):
        super().__init__(master.master,bg=BG_COLOR,bd=BD_SIZE)

        ###CANVAS###
        self.canv=tk.Canvas(self,bg=BG_COLOR,bd=BD_SIZE)
        self.canv.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)

        ###SCROLLBAR###
        self.sb=ttk.Scrollbar(self,orient=tk.VERTICAL,command=self.canv.yview)
        self.sb.pack(side=tk.RIGHT,fill=tk.Y)

        self.canv.configure(yscrollcommand=self.sb.set)
        self.canv.bind("<Configure>", lambda e:self.canv.configure(scrollregion=self.canv.bbox("all")))

        self.inner=tk.Frame(self.canv,bg=BG_COLOR,bd=BD_SIZE)

        self.canv.create_window((0,0),window=self.inner,anchor="nw")
        
        ###ADD HEADERS###
        idLbl=tk.Label(self.inner,font=stdFont,text="ID",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=5)
        cidLbl=tk.Label(self.inner,font=stdFont,text="ID KARNETU",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=12)
        numLbl=tk.Label(self.inner,font=stdFont,text="OPERACJA",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=27)
        dateLbl=tk.Label(self.inner,font=stdFont,text="DATA OPERACJI",bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=15)

        idLbl.grid(row=0,column=0,sticky=tk.EW)
        cidLbl.grid(row=0,column=1,sticky=tk.EW)
        numLbl.grid(row=0,column=2,sticky=tk.EW)
        dateLbl.grid(row=0,column=3,sticky=tk.EW)

    def add(self,row):
        row.idLbl.grid(row=CarnLogTable.iter,column=0,sticky=tk.EW)
        row.cidLbl.grid(row=CarnLogTable.iter,column=1,sticky=tk.EW)
        row.numLbl.grid(row=CarnLogTable.iter,column=2,sticky=tk.EW)
        row.dateLbl.grid(row=CarnLogTable.iter,column=3,sticky=tk.EW)
        
        CarnLogTable.iter+=1
        CarnLogTable.rows.append(row)

        ###MOVE SCROLLBAR###
        self.canv.configure(scrollregion=self.canv.bbox("all"))
        self.canv.yview("moveto",0.9)

    
    def load(self):
        logWrite("INFO","Loading carnets logs...")
        if os.path.isfile(CARNL_PATH):
            try:
                with open(CARNL_PATH) as out:
                    buff=out.read().split(";")
                    for i in buff[:-1]:
                        carnLog=i.split("^")
                        int(carnLog[0])
                        self.add(CarnLogRow(self.inner,CarnetLog(carnLog[0],int(carnLog[1]),carnLog[2])))
                logWrite("INFO","carnLog.txt loaded successfully.")
                
            except:
                logWrite("WARNING","carnLog.txt is broken. Loading denied! To regain your data use backup file!\n")
                global recError
                global recMessage
                recError,recMessage=True,"Błąd wczytywania bazy danych operacji karnetów."

    def save(self):
        
        
        with open(BUFFERS_PATH+"carnLogBuffer.txt","w") as out:
            out.truncate()
        try:
            with open(BUFFERS_PATH+"carnLogBuffer.txt","a") as out:
                for i in CarnLogTable.rows:
                    buffer=i.cidVar.get()+"^"+str(i.value)+"^"+i.dateVal.get()+";"
                    out.write(buffer)
            shutil.copy(BUFFERS_PATH+"carnLogBuffer.txt",CARNL_PATH)
            logWrite("INFO","Changes in carnes're logs saved.")
        except:
            logWrite("WARNING","Wrong rows format. Save denied!")
            global recError
            global recMessage
            recError,recMessage=True,"Błąd zapisu bazy danych operacji karnetów."
            return
        

###SLAVE WINDOWS###
class UpdateWindow():
    def __init__(self,cpt,bg=BG_COLOR,bd=BD_SIZE):
        self.master=tk.Tk()
        self.master.title(cpt)
        self.master.geometry("500x200")
        setActive(self.master)
        
        Window.otherWindows[Window.it]=self.master
        self.winId=Window.it
        Window.it+=1

        ###BINDING###
        self.master.bind("<Escape>",self.exit)

    def exit(self,event):
        del Window.otherWindows[self.winId]
        self.master.destroy()

    def run(self):
        self.master.mainloop()        



class UpdateCosm(UpdateWindow):
    def __init__(self,master,master2):

        super().__init__("Aktualizuj stan",bg=BG_COLOR,bd=BD_SIZE)
        self.master.geometry("450x380")
        self.tables=master
        self.history=master2
        self.fr=tk.Frame(self.master,bg=BG_COLOR)
        
        ###VARIABLES###
        self.passedAm=tk.StringVar(self.fr)
        self.passedDt=tk.StringVar(self.fr)
        self.cbTxt=tk.StringVar(self.fr)
        self.errMessage=tk.StringVar(self.fr)

        self.cosmId=0
        self.sellInt=tk.IntVar(self.fr)
        self.buyInt=tk.IntVar(self.fr)
        ###COMBOBOX###
        self.combobox=ttk.Combobox(self.fr,textvariable=self.cbTxt,width=20,font=stdFont)
        
        self.combobox['values']=[i.name for i in cosmetics]
        self.combobox.current(0)

        ###LABELS###
        self.cmTxt=tk.Label(self.fr,text="Kosmetyk:",bg=BG_COLOR,fg=FONT_COLOR,font=stdFont)
        self.ammTxt=tk.Label(self.fr,text="Ilość:",bg=BG_COLOR,fg=FONT_COLOR,font=stdFont)
        self.errMsgLbl=tk.Label(self.fr,textvariable=self.errMessage,fg="black",bg="white")

        ###ENTRIES###
        self.ammount=tk.Entry(self.fr,textvariable=self.passedAm,fg=FONT_COLOR,bg=BG_COLOR,width=22,font=stdFont)
        self.ammount.focus_set()


        ###BUTTON###
        self.agrBn=tk.Button(self.fr,text="Potwierdź",command=self.do,bg=BG_COLOR,fg=FONT_COLOR,font=stdFont,width=10,height=2)
    
        ###CHECKBOX###
        self.sell=tk.Checkbutton(self.fr,text="Sprzedane",variable=self.sellInt,onvalue=1,offvalue=0,command=lambda: self.discard(True),fg=FONT_COLOR,bg=BG_COLOR,selectcolor=BG_COLOR)
        self.buy=tk.Checkbutton(self.fr,text="Kupione",variable=self.buyInt,onvalue=1,offvalue=0,command=lambda:self.discard(False),fg=FONT_COLOR,bg=BG_COLOR,selectcolor=BG_COLOR)
        self.sell.select()

        ###CALENDAR###
        self.cal=tkc.Calendar(self.fr,selectmode="day",day=today.day,month=today.month,year=today.year)

        ###PACKING###
        self.fr.pack(fill=tk.BOTH,expand=1)
        self.combobox.grid(row=0,column=1,sticky=tk.W,pady=(5,2))
        self.cmTxt.grid(row=0,column=0,padx=(4,10),sticky=tk.E,pady=(5,2))
        self.ammTxt.grid(row=1,column=0,padx=(4,10),sticky=tk.E)
        self.ammount.grid(row=1,column=1,sticky=tk.W)
        self.sell.grid(row=1,column=2,sticky=tk.W)
        self.buy.grid(row=1,column=3,sticky=tk.W)
        self.cal.grid(row=2,column=1,columnspan=3,pady=10,sticky=tk.W)
        self.errMsgLbl.grid(row=3,column=1,columnspan=2)
        self.agrBn.grid(row=4,column=1,columnspan=2)

        self.fr.grid_rowconfigure(3,minsize=50)

        ###BINDING###
        self.master.bind("<Return>",self.do)



    def discard(self,choice):
        if choice:
            if not self.sellInt.get():
                self.sell.select()
            self.buy.deselect()
        else:
            if not self.buyInt.get():
                self.buy.select()
            self.sell.deselect()

    def target(self):
        choice=normalizeName(self.combobox.get())
        for i in cosmetics:
            if choice==i.name:
                self.cosmId=i.id
                return True
        return False     


    def do(self,event=None):
        ###GET VALUES###
        if not self.target():
            self.errMessage.set("Podaj nazwę kosmetyku z bazy!")
            return
            
        try:
            value=int(self.passedAm.get())
        except:
            self.errMessage.set("Podaj poprawną ilość!\nMusi to być liczba naturalna!")
            return
        if value<=0:
            self.errMessage.set("Ilość nie może być liczbą niedodatnią!")
            return

        if self.sellInt.get():
            value*=-1

        date=self.cal.selection_get().strftime(dateFormat)
        name=normalizeName(self.combobox.get())

        ###UPDATE COSMETICLOG###
        self.history.add(CosmLogRow(self.history.inner,CosmeticLog(name,value,date)))

        ###UPDATE COSMETIC TABLE###
        for i in cosmetics:
            if self.cosmId==i.id:
                i.update(value)
                break
        
        for i in self.tables.rows:
            if self.cosmId==i.id:
                i.update()
        
        
        self.master.destroy()



class UpdateCarn(UpdateWindow):
    def __init__(self,master,master2):

        super().__init__("Aktualizuj stan")
        self.master.geometry("550x400")
        self.tables=master
        self.history=master2

        self.fr=tk.Frame(self.master,bg=BG_COLOR,bd=BD_SIZE)
        self.fr.pack(fill=tk.BOTH,expand=1)
        ###VARIABLES###

        self.timeVar=tk.StringVar(self.master)
        self.idVar=tk.StringVar(self.master)
        self.nameVar=tk.StringVar(self.master)
        self.errMessage=tk.StringVar(self.master)
        
        self.nameVar.set("")
        self.errMessage.set("")
        ###LABELS###
        self.idLbl=tk.Label(self.fr,text="Id karnetu:",fg=FONT_COLOR,bg="white",font=stdFont)
        self.nameLbl=tk.Label(self.fr,text="Właściciel:",fg=FONT_COLOR,bg="white",font=stdFont)
        self.personLbl=tk.Label(self.fr,textvariable=self.nameVar,fg=FONT_COLOR,bg="white",font=stdFont)
        self.timeLbl=tk.Label(self.fr,text="Czas:",fg=FONT_COLOR,bg="white",font=stdFont)
        self.unitLbl=tk.Label(self.fr,text="min",fg=FONT_COLOR,bg="white",font=stdFont)
        self.errMsgLbl=tk.Label(self.fr,textvariable=self.errMessage,fg=FONT_COLOR,bg="white")

        ###ENTRIES###
        self.idEnt=tk.Entry(self.fr,textvariable=self.idVar,bg=BG_COLOR,fg=FONT_COLOR,font=stdFont,width=23)
        self.timeEnt=tk.Entry(self.fr,textvariable=self.timeVar,bg=BG_COLOR,fg=FONT_COLOR,font=stdFont,width=23)
        self.idEnt.focus_set()

        ###BUTTON###
        self.agrBn=tk.Button(self.fr,text="Potwierdź",command=self.do,bg=BG_COLOR,fg=FONT_COLOR,font=stdFont,width=10,height=2)
    
        ###CALENDAR###
        self.cal=tkc.Calendar(self.fr,selectmode="day",day=today.day,month=today.month,year=today.year)

        ###PACKING###
        self.idLbl.grid(row=0,column=0,padx=(4,10),sticky=tk.E,pady=(2,5))
        self.idEnt.grid(row=0,column=1,pady=(2,5))
        self.nameLbl.grid(row=0,column=2,sticky=tk.E,pady=(2,5))
        self.personLbl.grid(row=0,column=3,pady=(2,5),sticky=tk.E)
        self.timeLbl.grid(row=1,column=0,padx=(4,10),sticky=tk.E,pady=(2,5))
        self.timeEnt.grid(row=1,column=1,pady=(2,5))
        self.unitLbl.grid(row=1,column=2,sticky=tk.W,pady=(2,5))
        self.cal.grid(row=2,column=1,columnspan=2,pady=10,sticky=tk.W)
        self.errMsgLbl.grid(row=3,column=1,columnspan=2)
        self.agrBn.grid(row=4,column=1,columnspan=2)

        self.fr.grid_rowconfigure(3,minsize=50)


        ###BINDING###
        self.master.bind("<Return>",self.do)
        self.idEnt.bind("<KeyRelease>",self.getPerson)

    def getPerson(self,event=None):
        buff=self.idVar.get()
        buff=normalizeName(buff)
        for i in carnets:
            if i.id==buff:
                self.nameVar.set(i.name)
                return
        self.nameVar.set("")
        

    def do(self,event=None):
        ###GET VALUES###
        buff=self.idVar.get()
        time=self.timeVar.get()
        if buff=="":
            self.errMessage.set("Wprowadź identyfikator!")
            return
        
        try:
            int(buff)
        except:
            self.errMessage.set("Nieprawidłowy identyfikator!")
            return
        
        if self.nameVar.get()=="":
            self.errMessage.set("W bazie nie figuruje karnet\no podanym id!")
            return
        

        
        if time=="":
            self.errMessage.set("Wprowadź czas pobytu na solarium!")
            return
        try:
            time=int(time)
        except:
            self.errMessage.set("Czas musi być przedstawiony\nw postaci liczby naturalnej!")
            return
        if time<=0:
            self.errMessage.set("Czas nie może być\nliczbą niedodatnią!")
            return
            

        date=self.cal.selection_get()

        ###UPDATE CARNETLOG###
        self.history.add(CarnLogRow(self.history.inner,CarnetLog(buff,time,date)))

        ###UPDATE CARNET TABLE###
        for i in carnets:
            if buff==i.id:
                i.update(time)
                break

        for i in self.tables.rows:
            if buff==i.id:
                i.update()
                
        self.master.destroy()


class AddCosm(UpdateWindow):
    def __init__(self,master,master2):
        super().__init__("Dodaj kosmetyk")
        self.master.geometry("450x380")

        ###VARIABLES###
        self.nametxt=tk.StringVar(self.master)
        self.errMessage=tk.StringVar(self.master)
        self.errMessage.set("")

        self.cosmTable=master
        self.logTable=master2

        self.fr=tk.Frame(self.master,bg=BG_COLOR,bd=BD_SIZE)
        self.fr.pack(fill=tk.BOTH,expand=1)

        self.name=tk.Label(self.fr,text="Nazwa\nkosmetyku:",bg=BG_COLOR,fg=FONT_COLOR,font=stdFont)
        self.nameEnt=tk.Entry(self.fr,textvariable=self.nametxt,bg=BG_COLOR,fg=FONT_COLOR,width=20,font=stdFont)
        self.nameEnt.focus_set()
        self.errMsgLbl=tk.Label(self.fr,textvariable=self.errMessage,bg=BG_COLOR,fg=FONT_COLOR)

        self.agrBn=tk.Button(self.fr,text="Potwierdź",command=self.do,bg=BG_COLOR,fg=FONT_COLOR,font=stdFont,width=10,height=2)
        
        ###CALENDAR###
        self.cal=tkc.Calendar(self.fr,selectmode="day",day=today.day,month=today.month,year=today.year)
        
        ###PACKING###
        self.name.grid(row=0,column=0,padx=(4,10),pady=(5,2))
        self.nameEnt.grid(row=0,column=1,pady=(5,2),sticky=tk.W)
        self.cal.grid(row=1,column=1,columnspan=3,pady=10)
        self.agrBn.grid(row=3,column=1,columnspan=3)
        self.errMsgLbl.grid(row=2,column=1,columnspan=3)
        self.fr.grid_rowconfigure(2,minsize=50)
        #self.fr.grid_columnconfigure(2,weight=2)   

        ###BINDING###
        self.master.bind("<Return>",self.do)


    def do(self,event=None):
        ###CHECK IF ENTRY IS CORRECT###
        buff=self.nametxt.get()
        if buff=="":
            self.errMessage.set("Nazwa nie może być pusta!")
            return
        
        
        empty=True
        for i in buff:
            if (ord(i)>64 and ord(i)<91) or (ord(i)>96 and ord(i)<123):
                empty=False
                break
        if empty:
            self.errMessage.set("Nazwa musi zawierać\nconajmniej jedną literę!")
            return
        
        for i in buff:
            if i=="^":
                self.errMessage.set("Nazwa zawiera niedozwolony znak '^' !")
                return

        
        ###NORMALIZE NAME###
        buff=normalizeName(buff)
        for i in cosmetics:
            i=i.name
            if i==buff:
                self.errMessage.set("W bazie istnieje już\ntaki kosmetyk!")
                return
        
        date=self.cal.selection_get().strftime(dateFormat)

        ###STORE DATA###
        self.cosmTable.add(CosmRow(self.cosmTable.inner,Cosmetic(buff)))
        self.logTable.add(CosmLogRow(self.logTable.inner,CosmeticLog(buff,0,date)))

        self.master.destroy()


class AddCarn(UpdateWindow):
    def __init__(self,master,master2):
        super().__init__("Dodaj karnet")

        self.master.geometry("450x300")

        ###VARIABLES###
        self.nameVar=tk.StringVar(self.master)
        self.idVar=tk.StringVar(self.master)
        self.timeVar=tk.StringVar(self.master)
        self.errMessage=tk.StringVar(self.master)
        self.errMessage.set("")

        self.carnTable=master
        self.logTable=master2

        self.fr=tk.Frame(self.master,bg="white")
        self.fr.pack(fill=tk.BOTH,expand=1)

        ###LABELS###
        self.idLbl=tk.Label(self.fr,text="Identyfikator karntetu:",bg="white",fg="black",font=stdFont)
        self.nameLbl=tk.Label(self.fr,text="Imię:",bg="white",fg="black",font=stdFont)
        self.snameLbl=tk.Label(self.fr,text="Nazwisko:",bg="white",fg="black",font=stdFont)
        self.timeLbl=tk.Label(self.fr,text="Na ile minut:",bg="white",fg="black",font=stdFont)
        self.errMsgLbl=tk.Label(self.fr,textvariable=self.errMessage,fg="black",bg="white",font=stdFont)


        ###ENTRIES###        
        self.idEnt=tk.Entry(self.fr,textvariable=self.idVar,bg=BG_COLOR,fg=FONT_COLOR,width=23,font=stdFont)
        self.nameEnt=tk.Entry(self.fr,bg=BG_COLOR,fg=FONT_COLOR,width=23,font=stdFont)
        self.snameEnt=tk.Entry(self.fr,bg=BG_COLOR,fg=FONT_COLOR,width=23,font=stdFont)
        self.timeEnt=tk.Entry(self.fr,textvariable=self.timeVar,bg=BG_COLOR,fg=FONT_COLOR,width=23,font=stdFont)
        self.idEnt.focus_set()

        ###BUTTON###
        self.agrBn=tk.Button(self.fr,text="Potwierdź",command=self.do,bg="white",fg=FONT_COLOR,font=stdFont,width=10,height=2)
        
        ###PACKING###
        self.idLbl.grid(row=0,column=0,padx=(4,10),pady=(5,2),sticky=tk.E)
        self.idEnt.grid(row=0,column=1,pady=(5,2))
        self.nameLbl.grid(row=1,column=0,padx=(4,10),pady=(5,2),sticky=tk.E)
        self.nameEnt.grid(row=1,column=1)
        self.snameLbl.grid(row=2,column=0,padx=(4,10),pady=(5,2),sticky=tk.E)
        self.snameEnt.grid(row=2,column=1)
        self.timeLbl.grid(row=3,column=0,padx=(4,10),pady=(5,2),sticky=tk.E)
        self.timeEnt.grid(row=3,column=1)
        self.errMsgLbl.grid(row=4,column=1)
        self.agrBn.grid(row=5,column=1)
        
        self.fr.grid_rowconfigure(4,minsize=50)

        
        ###BINDING###
        self.master.bind("<Return>",self.do)


    def do(self,event=None):

        ###CHECK IF ENTRIES ARE CORRECT###
        buff=self.idEnt.get()
        if buff=="":
            self.errMessage.set("Podaj identyfikator!")
            return
        
        try:
            int(buff)
        except:
            self.errMessage.set("Identyfikator składa się\nwyłącznie z liczb!")
            return
        

        name=self.nameEnt.get()
        if name=="":
            self.errMessage.set("Podaj imię!")
            return
        
        name=normalizeName(name)

        for i in name:
            if (ord(i)<65) or (ord(i)>90 and ord(i)<97):
                self.errMessage.set("Imię może składać się\ntylko z liter!")
                return
        
        surename=self.snameEnt.get()
        if surename=="":
            self.errMessage.set("Podaj nazwisko!")
            return
        
        surename=normalizeName(surename)

        for i in surename:
            if (ord(i)<65) or (ord(i)>90 and ord(i)<97):
                self.errMessage.set("Nazwisko może składać się\ntylko z liter!")
                return
        
        minutes=self.timeVar.get()
        if minutes=="":
            self.errMessage.set("Podaj ilość minut na karnecie!")
            return
        
        try:
            minutes=int(minutes)
        except:
            self.errMessage.set("Ilość minut musi być podana\nw postaci liczby całkowitej!")
            return

        ###NORMALIZE ID###
        buff=normalizeName(buff)
        for i in carnets:
            i=i.id
            if i==buff:
                self.errMessage.set("W bazie istnieje już karnet o podanym id!")
                return
        
        ###STORE DATA###
        self.carnTable.add(CarnRow(self.carnTable.inner,Carnet(buff,name,surename,minutes)))
        self.logTable.add(CarnLogRow(self.logTable.inner,CarnetLog(buff,0,today.strftime(dateFormat))))

        self.master.destroy()

class RemoveCarn(UpdateWindow):
    def __init__(self,master,master2):

        super().__init__("Usuń karnet")
        self.master.geometry("500x350")
        self.tables=master
        self.history=master2

        self.fr=tk.Frame(self.master,bg=BG_COLOR,bd=BD_SIZE)
        self.fr.pack(fill=tk.BOTH,expand=1)
        ###VARIABLES###

        self.idVar=tk.StringVar(self.master)
        self.nameVar=tk.StringVar(self.master)
        self.errMessage=tk.StringVar(self.master)
        
        self.nameVar.set("")
        self.errMessage.set("")
        ###LABELS###
        self.idLbl=tk.Label(self.fr,text="Id karnetu:",fg=FONT_COLOR,bg="white",font=stdFont)
        self.nameLbl=tk.Label(self.fr,text="Właściciel:",fg=FONT_COLOR,bg="white",font=stdFont)
        self.personLbl=tk.Label(self.fr,textvariable=self.nameVar,fg=FONT_COLOR,bg="white",font=stdFont)

        self.errMsgLbl=tk.Label(self.fr,textvariable=self.errMessage,fg=FONT_COLOR,bg="white")

        ###ENTRY###
        self.idEnt=tk.Entry(self.fr,textvariable=self.idVar,width=23,bg=BG_COLOR,fg=FONT_COLOR)
        self.idEnt.focus_set()

        ###BUTTON###
        self.agrBn=tk.Button(self.fr,text="Potwierdź",command=self.do,font=stdFont,width=10,height=2,bg=BG_COLOR,fg=FONT_COLOR)
    
        ###CALENDAR###
        self.cal=tkc.Calendar(self.fr,selectmode="day",day=today.day,month=today.month,year=today.year)

        ###PACKING###
        self.idLbl.grid(row=0,column=0,padx=(4,10),pady=(5,2),sticky=tk.E)
        self.idEnt.grid(row=0,column=1,pady=(5,2))
        self.nameLbl.grid(row=0,column=2,pady=(5,2))
        self.personLbl.grid(row=0,column=3,pady=(5,2))
        self.cal.grid(row=1,column=1,columnspan=2,sticky=tk.W,pady=10)
        self.errMsgLbl.grid(row=2,column=1,columnspan=2)
        self.agrBn.grid(row=3,column=1,columnspan=2)

        self.fr.grid_rowconfigure(2,minsize=50)



        ###BINDING###
        self.master.bind("<Return>",self.do)
        self.idEnt.bind("<KeyRelease>",self.getPerson)

    def getPerson(self,event=None):
        buff=self.idVar.get()
        buff=normalizeName(buff)
        for i in carnets:
            if i.id==buff:
                self.nameVar.set(i.name)
                return
        self.nameVar.set("")
        

    def do(self,event=None):

        ###GET VALUES###
        buff=self.idVar.get()
        if buff=="":
            self.errMessage.set("Wprowadź identyfikator!")
            return
        
        try:
            int(buff)
        except:
            self.errMessage.set("Nieprawidłowy identyfikator!")
            return
        
        if self.nameVar.get()=="":
            self.errMessage.set("W bazie nie figuruje\nkarnet o podanym id!")
            return
            
        ###UPDATE CARNETLOG###
        date=self.cal.selection_get().strftime(dateFormat)
        self.history.add(CarnLogRow(self.history.inner,CarnetLog(buff,-1,date)))

        ###UPDATE CARNET TABLE###
        for i in carnets:
            if buff==i.id:
                carnets.remove(i)
                break

        for i in self.tables.rows:
            if buff==i.id:
                i.clear()
                self.tables.rows.remove(i)
                
        self.master.destroy()
    

class CosmRow():
    def __init__(self,master,cosmetic,date=None):
        
        self.fr=master

        ###VARIABLES###
        self.amnVar=tk.IntVar(self.fr)
        self.amnVar.set(cosmetic.count)
        self.nameVar=tk.StringVar(self.fr)
        self.nameVar.set(cosmetic.name)
        self.id=cosmetic.id
        self.lastUpdateVal=tk.StringVar(self.fr)
        self.thisMntVar=tk.StringVar(self.fr)
        self.thisMntVar.set(self.thisMonth())

        if date:
            self.lastUpdateVal.set(date)
        else:
            self.lastUpdateVal.set(today.strftime(dateFormat))

        ###LABELS###
        self.idLbl=tk.Label(self.fr,text=cosmetic.id,bg="white",fg="black",bd=BD_SIZE,font=stdFont,relief="solid",width=5)
        self.name=tk.Label(self.fr,textvariable=self.nameVar,bg="white",fg="black",font=stdFont,bd=BD_SIZE,relief="solid",width=20)
        self.amn=tk.Label(self.fr,textvariable=self.amnVar,bg="white",fg="black",font=stdFont,bd=BD_SIZE,relief="solid",width=6)
        self.lstUpdLbl=tk.Label(self.fr,textvariable=self.lastUpdateVal,bg="white",fg="black",font=stdFont,bd=BD_SIZE,relief="solid",width=18)
        self.thisMntLbl=tk.Label(self.fr,textvariable=self.thisMntVar,bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,font=stdFont,relief="solid",width=17)

    def thisMonth(self):
        out=0
        for i in cosmeticLogs:
            if i.name==self.nameVar.get():
                if i.date[:7]==today.strftime(thisMonthFormat):
                    out+=i.action
        return str(out)


    def update(self):
        for i in cosmetics:
            if i.id==self.id:
                self.amnVar.set(i.count)
                self.lastUpdateVal.set(today.strftime(dateFormat))
                self.thisMntVar.set(self.thisMonth())
                return

    def clear(self):
        self.idLbl.grid_remove()
        self.name.grid_remove()
        self.amn.grid_remove()
        self.lstUpdLbl.grid_remove()
        self.thisMntLbl.grid_remove()


class CarnRow():
    def __init__(self,master,carnet,date=None):
        super().__init__()

        self.fr=master

        ###VARIABLES###
        self.minutesVar=tk.IntVar(self.fr)
        self.minutesVar.set(carnet.minutes)
        self.total=carnet.total
        self.id=carnet.id
        self.color=UNACTIVE_COLOR
        self.lastUpdateVal=tk.StringVar(self.fr)
        self.person=carnet.name
        self.timeVar=tk.StringVar(self.fr)
        self.timeVar.set(str(self.minutesVar.get())+"/"+str(self.total))
        if date:
            self.lastUpdateVal.set(date)
        else:
            self.lastUpdateVal.set(today.strftime(dateFormat))
        
        ###LABELS###
        self.idLbl=tk.Label(self.fr,text=carnet.id,bg=self.color,fg=FONT_COLOR,font=stdFont,bd=BD_SIZE,relief="solid",width=6)
        self.prsnLbl=tk.Label(self.fr,text=self.person,bg=self.color,fg=FONT_COLOR,font=stdFont,bd=BD_SIZE,relief="solid",width=29)
        self.usertimeLbl=tk.Label(self.fr,textvariable=self.timeVar,bg=self.color,fg=FONT_COLOR,font=stdFont,bd=BD_SIZE,relief="solid",width=13)
        self.lstUpdLbl=tk.Label(self.fr,textvariable=self.lastUpdateVal,bg=self.color,fg=FONT_COLOR,font=stdFont,bd=BD_SIZE,relief="solid",width=18)
        
        self.limit(carnet.overtime)


    def limit(self,overtime):
        if overtime:
            self.color=LIMIT_COLOR
        else:
            self.color=UNACTIVE_COLOR
        self.idLbl.config(bg=self.color)
        self.prsnLbl.config(bg=self.color)
        self.usertimeLbl.config(bg=self.color)
        self.lstUpdLbl.config(bg=self.color)
            

    def update(self):
        for i in carnets:
            if i.id==self.id:
                self.minutesVar.set(i.minutes)
                self.timeVar.set(str(self.minutesVar.get())+"/"+str(self.total))
                self.limit(i.overtime)
                self.lastUpdateVal.set(today.strftime(dateFormat))
                return
    
    def clear(self):
        self.idLbl.grid_remove()
        self.prsnLbl.grid_remove()
        self.usertimeLbl.grid_remove()
        self.lstUpdLbl.grid_remove()



class CosmLogRow():
    def __init__(self,master,cosmeticLog):
        super().__init__()

        self.fr=master

        ###VARIABLES###
        self.value=cosmeticLog.action
        self.nameVar=tk.StringVar(self.fr)
        self.nameVar.set(cosmeticLog.name)
        self.dateVal=tk.StringVar(self.fr)
        self.dateVal.set(cosmeticLog.date)

        ###LABELS###
        self.idLbl=tk.Label(self.fr,text=cosmeticLog.id,bg="white",fg="black",font=stdFont,bd=BD_SIZE,relief="solid",width=5)
        self.name=tk.Label(self.fr,textvariable=self.nameVar,bg="white",fg="black",font=stdFont,bd=BD_SIZE,relief="solid",width=20)
        self.amn=tk.Label(self.fr,text=self.getVal(self.value),bg="white",fg="black",font=stdFont,bd=BD_SIZE,relief="solid",width=19)
        self.dateLbl=tk.Label(self.fr,textvariable=self.dateVal,bg="white",fg="black",font=stdFont,bd=BD_SIZE,relief="solid",width=15)

    def getVal(self,num):
        if num==0:  return "Dodany nowy kosmetyk"
        elif num<0: return "Sprzedano: {}".format(-1*num)
        else:       return "Kupiono: {}".format(num)

    def clear(self):
        self.idLbl.grid_remove()
        self.name.grid_remove()
        self.amn.grid_remove()
        self.dateLbl.grid_remove()



class CarnLogRow():
    def __init__(self,master,carnetLog):

        self.fr=master

        ###VARIABLES###
        self.value=carnetLog.num
        self.dateVal=tk.StringVar(self.fr)
        self.dateVal.set(carnetLog.date)
        self.cidVar=tk.StringVar(self.fr)
        self.cidVar.set(carnetLog.cardId)


        ###LABELS###
        self.idLbl=tk.Label(self.fr,text=carnetLog.id,font=stdFont,bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=5)
        self.cidLbl=tk.Label(self.fr,textvariable=self.cidVar,font=stdFont,bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=12)
        self.numLbl=tk.Label(self.fr,text=self.getVal(),font=stdFont,bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=27)
        self.dateLbl=tk.Label(self.fr,textvariable=self.dateVal,font=stdFont,bg=BG_COLOR,fg=FONT_COLOR,bd=BD_SIZE,relief="solid",width=15)

        
    def getVal(self):
        if self.value>0:
            return "Wykorzystano {} min.".format(self.value)
        elif not self.value:
            return "Dodano do bazy nowy karnet."
        else:
            return "Usunięto z bazy karnet {}".format(self.cidVar.get())
    
    def clear(self):
        self.idLbl.grid_remove()
        self.cidLbl.grid_remove()
        self.numLbl.grid_remove()
        self.dateLbl.grid_remove()



###CLASSESS###
class Cosmetic():
    id=1

    def __init__(self,name,val=0):
        self.id=Cosmetic.id
        self.name=name
        self.count=val
        cosmetics.append(self)
        Cosmetic.id+=1
        
        Window.actionStack.append({
        "Action":"Add",
        "Object":"Cosmetic",
        "ItemId":self.id,
        "Ammount":0})
    
    def __str__(self):
        return "Nazwa:{}\tStan:{}".format(self.name,self.count)
    
    def update(self,num):
        self.count+=num
        Window.actionStack.append({
        "Action":"Update",
        "Object":"Cosmetic",
        "ItemId":self.id,
        "Ammount":num})
    

class Carnet():
    def __init__(self,id_,name,surename,total,minutes=None):
        self.id=id_
        self.name=name+" "+surename
        self.total=total
        
        if minutes:
            if not type(minutes)==type(1):
                minutes=int(minutes)

            self.minutes=minutes
            if minutes<0:
                self.overtime=True
            else:
                self.overtime=False
        else:
            self.minutes=total
            self.overtime=False
        carnets.append(self)

        Window.actionStack.append({
        "Action":"Add",
        "Object":"Carnet",
        "ItemId":self.id,
        "Ammount":0})
    
    def __str__(self):
        return "Karnet:{}\tOsoba:{}\tLiczba godzin:{}\tPozostała liczba godzin:{}".format(self.id,self.name,self.total,self.minutes)

    def update(self,num):
        self.minutes-=num
        if self.minutes<0:
            self.overtime=True
        else:
            self.overtime=False
        Window.actionStack.append({
        "Action":"Update",
        "Object":"Carnet",
        "ItemId":self.id,
        "Ammount":num})
    
    def __del__(self):
        Window.actionStack.append({
        "Action":"Delete",
        "Object":"Carnet",
        "ItemId":self.id,
        "Ammount":{
            "Person":self.name,
            "Total":self.total,
            "Minutes":self.minutes
        }})
        
###LOGS###
class CosmeticLog():
    id=1
    def __init__(self,cosmetic,num,date):
        self.id=CosmeticLog.id
        CosmeticLog.id+=1
        self.name=cosmetic
        self.action=num
        self.date=date
        cosmeticLogs.append(self)
    
    def __str__(self):
        return "id:{}\tkosmetyk:{}\tzmiana stanu:{}\tdata:{}".format(self.id,self.name,self.action,self.date)
    
class CarnetLog():
    id=1
    def __init__(self,cardId,num,date):
        self.id=CarnetLog.id
        CarnetLog.id+=1
        self.cardId=cardId
        self.num=num
        self.date=date
        carnetLogs.append(self)
    
    def __str__(self):
        if num>0:
            return "id:{}\tid karnetu:{}\tczas pobytu:{}\tdata:{}".format(self.id,self.cardId,self.num,self.date)
        if not num:
            return "id:{}\tid karnetu:{}\tdodano karnet\tdata:{}".format(self.id,self.cardId,self.date)
        if num<0:
            return "id:{}\tid karnetu:{}\tusunięto karnet\tdata:{}".format(self.id,self.cardId,self.date)



###MAIN###
def main():

    checkPaths()
    clearLogs(LOGS_PATH,20)
    clearLogs(PLOTS_LOGS_PATH,20)


    root=Window("Pawcio Counter")
    menu=Menu(root.menu,root)
    table1=CosmTable(root.table)
    table2=CosmLogTable(root.oper)
    table3=CarnTable(root.table)
    table4=CarnLogTable(root.oper)
    cosmActions=ActionMenu(root.actPan,table1,table2,table3,table4)
    carnActions=CActionMenu(root.actPan,table3,table4)

    ###STORE FRAMES###
    root.rememberFrame(table1)
    root.rememberFrame(table3)
    root.rememberFrame(table2)
    root.rememberFrame(table4)
    root.rememberFrame(cosmActions)
    root.rememberFrame(carnActions)

    table2.load()
    table1.load()
    table3.load()
    table4.load()
    Window.actionStack=[]
    
    root.addFrame(0,menu)
    root.addFrame(1,table1)
    root.addFrame(2,table2)
    root.addFrame(3,cosmActions)

    root.run()


###EXECUTION###
if __name__=="__main__":
    main()