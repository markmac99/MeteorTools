#
# UI to manage fireball data collection
# Copyright (C) 2018-2023 Mark McIntyre
#
import os
import sys
import argparse
import logging
import logging.handlers
import datetime
import configparser
import shutil
import platform
import subprocess
import glob
import xmltodict

import boto3
import paramiko
from scp import SCPClient

import tkinter as tk
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
from tkinter import StringVar, Frame, ACTIVE, END, Listbox, Menu, Entry, Button
from tkinter.ttk import Label, Style, LabelFrame, Scrollbar

from PIL import Image as img
from PIL import ImageTk

from meteortools.ukmondb import getLiveJpgs, createTxtFile


config_file = ''
noimg_file = ''
global_bg = "Black"
global_fg = "Gray"


def quitApp():
    # Cleanly exits the app
    root.quit()
    root.destroy()


def log_timestamp():
    """ Returns timestamp for logging.
    """
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


class StyledButton(Button):
    """ Button with style. 
    """
    def __init__(self, *args, **kwargs):
        Button.__init__(self, *args, **kwargs)

        self.configure(foreground = global_fg, background = global_bg, borderwidth = 3)


class StyledEntry(Entry):
    """ Entry box with style. 
    """
    def __init__(self, *args, **kwargs):
        Entry.__init__(self, *args, **kwargs)

        self.configure(foreground = global_fg, background = global_bg, insertbackground = global_fg, disabledbackground = global_bg, disabledforeground = "DimGray")


class ConstrainedEntry(StyledEntry):
    """ Entry box with constrained values which can be input (e.g. 0-255).
    """
    def __init__(self, *args, **kwargs):
        StyledEntry.__init__(self, *args, **kwargs)
        self.maxvalue = 255
        vcmd = (self.register(self.on_validate), "%P")
        self.configure(validate="key", validatecommand=vcmd)
        # self.configure(foreground = global_fg, background = global_bg, insertbackground = global_fg)

    def disallow(self):
        """ Pings a bell on values which are out of bound.
        """
        self.bell()

    def update_value(self, maxvalue):
        """ Updates values in the entry box.
        """
        self.maxvalue = maxvalue
        vcmd = (self.register(self.on_validate), "%P")
        self.configure(validate="key", validatecommand=vcmd)

    def on_validate(self, new_value):
        """ Checks if entered value is within bounds.
        """
        try:
            if new_value.strip() == "":
                return True
            value = int(new_value)
            if value < 0 or value > self.maxvalue:
                self.disallow()
                return False
        except ValueError:
            self.disallow()
            return False

        return True


class fbCollector(Frame):
    def __init__(self, parent, patt=None):
        Frame.__init__(self, parent, bg = global_bg)
        parent.configure(bg = global_bg)  # Set backgound color
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self.grid(sticky="NSEW")  # Expand frame to all directions
        self.parent = parent

        self.fb_dir = ''
        self.upload_bucket = ''
        self.upload_folder = ''
        self.live_bucket = ''
        self.gmn_key = ''
        self.gmn_user = ''
        self.gmn_server = ''
        self.wmpl_loc = ''
        self.wmpl_env = ''
        self.rms_loc = ''
        self.rms_env = ''
        self.selected = {}
        self.evtMonTriggered = None
        self.review_stack = False

        self.readConfig()

        self.patt = patt
        if patt is None:
            self.dir_path = self.fb_dir
        else:
            self.dir_path = os.path.join(self.fb_dir, patt)
        log.info(f"Fireball folder is {self.fb_dir}")

        self.initUI()
        if self.dir_path != self.fb_dir:
            bin_list = self.get_bin_list()
            for b in bin_list:
                self.selected[b] = (0, '')
            self.update_listbox(bin_list)

        # Update UI changes
        parent.update_idletasks()
        parent.update()

        return 

    def readConfig(self):
        localcfg = configparser.ConfigParser()
        localcfg.read(config_file)
        print(f"Fireball folder is {localcfg['Fireballs']['basedir']}")
        self.fb_dir = localcfg['Fireballs']['basedir']
        self.upload_bucket = localcfg['Fireballs']['uploadbucket']
        self.upload_folder = localcfg['Fireballs']['uploadfolder']
        self.live_bucket = localcfg['Fireballs']['livebucket']

        try: 
            self.gmn_key = localcfg['Fireballs']['gmnkey']
            self.gmn_user = localcfg['Fireballs']['gmnuser']
            self.gmn_server = localcfg['Fireballs']['gmnserver']
        except:
            pass

        self.wmpl_loc = localcfg['Fireballs']['wmpl_loc']
        self.wmpl_env= localcfg['Fireballs']['wmpl_env']
        self.rms_loc = localcfg['Fireballs']['rms_loc']
        self.rms_env= localcfg['Fireballs']['rms_env']
        return

    def quitApplication(self):
        print('quitting')
        quitApp()

    def initUI(self):
        """ Initialize GUI elements.
        """

        self.parent.title("Fireball Downloader")

        # Configure the style of each element
        s = Style()
        s.configure("TButton", padding=(0, 5, 0, 5), font='serif 10') 
        s.configure('TLabelframe.Label', foreground=global_fg, background=global_bg)
        s.configure('TLabelframe', foreground =global_fg, background=global_bg, padding=(3, 3, 3, 3))
        s.configure("TRadiobutton", foreground = global_fg, background = global_bg)
        s.configure("TLabel", foreground = global_fg, background = global_bg)
        s.configure("TCheckbutton", foreground = global_fg, background = global_bg)
        s.configure("Vertical.TScrollbar", background=global_bg, troughcolor = global_bg)

        self.columnconfigure(0, pad=3)
        self.columnconfigure(1, pad=3)
        self.columnconfigure(2, pad=3)
        self.columnconfigure(3, pad=3)
        self.columnconfigure(4, pad=3)
        self.columnconfigure(5, pad=3)
        self.columnconfigure(6, pad=3)
        self.columnconfigure(7, pad=3)
        self.columnconfigure(8, pad=3)

        self.rowconfigure(0, pad=3)
        self.rowconfigure(1, pad=3)
        self.rowconfigure(2, pad=3)
        self.rowconfigure(3, pad=3)
        self.rowconfigure(4, pad=3)
        self.rowconfigure(5, pad=3)
        self.rowconfigure(6, pad=3)
        self.rowconfigure(7, pad=3)
        self.rowconfigure(8, pad=3)
        self.rowconfigure(9, pad=3)
        self.rowconfigure(10, pad=3)

        # Make menu
        self.menuBar = Menu(self.parent)
        self.parent.config(menu=self.menuBar)

        # File menu
        fileMenu = Menu(self.menuBar, tearoff=0)
        fileMenu.add_command(label="Load Folder", command=self.loadFolder)
        fileMenu.add_command(label="Delete Folder", command=self.delFolder)
        fileMenu.add_separator()
        fileMenu.add_command(label="Fetch GMN Data", command=self.getGMNData)
        fileMenu.add_separator()
        fileMenu.add_command(label="Update Watchlist", command=self.getWatchlist)
        fileMenu.add_command(label="View Watchlist", command=self.viewWatchlist)
        fileMenu.add_command(label="upload Watchlist", command=self.putWatchlist)
        fileMenu.add_command(label="Fetch Event Data", command=self.getEventData)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.quitApplication)
        self.menuBar.add_cascade(label="File", underline=0, menu=fileMenu)

        revMenu = Menu(self.menuBar, tearoff=0)
        revMenu.add_command(label="Review Stacks", command=self.checkStacks)
        self.menuBar.add_cascade(label="Review", underline=0, menu=revMenu)

        # buttons
        self.save_panel = LabelFrame(self, text=' Image Selection ')
        self.save_panel.grid(row = 1, columnspan = 2, sticky='WE')

        self.newpatt = StringVar()
        self.newpatt.set(self.patt)

        self.patt_entry = StyledEntry(self.save_panel, textvariable = self.newpatt, width = 20)
        self.patt_entry.grid(row = 1, column = 1, columnspan = 2, sticky = "W")
        save_bmp = StyledButton(self.save_panel, text="Get Images", width = 8, command = lambda: self.get_data())
        save_bmp.grid(row = 1, column = 3)

        save_bmp = StyledButton(self.save_panel, text="Remove Data", width = 8, command = lambda: self.remove_image())
        save_bmp.grid(row = 1, column = 4)
        save_bmp = StyledButton(self.save_panel, text="Clean Folder", width = 8, command = lambda: self.clean_folder())
        save_bmp.grid(row = 1, column = 5)
        

        # Listbox
        self.scrollbar = Scrollbar(self)
        self.listbox = Listbox(self, width = 47, yscrollcommand=self.scrollbar.set, exportselection=0, activestyle = "none", bg = global_bg, fg = global_fg)
        self.listbox.config(height = 25)  # Listbox size
        self.listbox.grid(row = 4, column = 0, rowspan = 7, columnspan = 2, sticky = "NS")  # Listbox position
        self.scrollbar.grid(row = 4, column = 2, rowspan = 7, sticky = "NS")  # Scrollbar size

        self.listbox.bind('<<ListboxSelect>>', self.update_image)
        self.scrollbar.config(command = self.listbox.yview)

        # IMAGE
        try:
            # Show the TV test card image on program start
            #noimage_data = img.open('noimage.bin').resize((640,360))
            noimgdata = img.open(noimg_file).resize((640,360))
            noimage = ImageTk.PhotoImage(noimgdata)
        except:
            noimage = None

        self.imagelabel = Label(self, image = noimage)
        self.imagelabel.image = noimage
        self.imagelabel.grid(row=3, column=3, rowspan = 4, columnspan = 3)

        # Timestamp label
        self.timestamp_label = Label(self, text = "CCNNNN YYYY-MM-DD HH:MM.SS.mms", font=("Courier", 12))
        self.timestamp_label.grid(row = 7, column = 3, sticky = "E")

    def get_bin_list(self):
        """ Get a list of image files in a given directory.
        """
        if self.dir_path is None:
            dirname = tkFileDialog.askdirectory(parent=root,initialdir=self.fb_dir,
                title='Please select a directory')    
            _, thispatt = os.path.split(dirname)
            self.dir_path = os.path.join(self.fb_dir, thispatt)
            self.patt = thispatt
            self.newpatt.set(self.patt)

        if self.review_stack is False:
            targdir = self.dir_path
        else:
            targdir = self.dir_path + '/stacks'
        bin_list = [line for line in os.listdir(targdir) if self.correct_datafile_name(line)]
        return bin_list

    def update_listbox(self, bin_list):
        """ Updates the listbox with the current entries.
        """
        self.listbox.delete(0, END)
        for line in sorted(bin_list):
            self.listbox.insert(END, line)
            if line not in self.selected:
                self.selected[line] = (0, '')
            print(line, self.selected[line])
            if self.selected[line][0] == 1:
                self.listbox.itemconfig(END, fg = 'green')

    def checkStacks(self):
        self.review_stack = True
        bin_list = self.get_bin_list()
        for b in bin_list:
            self.selected[b] = (0, '')
        self.update_listbox(bin_list)

    
    def loadFolder(self):
        self.review_stack = False
        self.dir_path = None
        bin_list = self.get_bin_list()
        for b in bin_list:
            self.selected[b] = (0, '')
        self.update_listbox(bin_list)

    def delFolder(self):
        noimgdata = img.open(noimg_file).resize((640,360))
        noimage = ImageTk.PhotoImage(noimgdata)
        self.imagelabel.configure(image = noimage)
        self.imagelabel.image = noimage
        if self.dir_path is not None and self.dir_path != self.fb_dir:
            try:
                shutil.rmtree(self.dir_path)
                self.dir_path = self.fb_dir
            except Exception as e:
                print(f'unable to remove {self.dir_path}')
                print(e)

    def correct_datafile_name(self, line):
        if '.jpg' in line and 'noimage' not in line:
            return True
        return False
    
    def removeRelated(self, imgname):
        camid = imgname[:6]
        mp4s = os.listdir(os.path.join(self.dir_path, 'mp4s'))
        badones = [x for x in mp4s if camid in x]
        for ba in badones:
            os.remove(os.path.join(self.dir_path, 'mp4s', ba))
        jpgs = os.listdir(os.path.join(self.dir_path, 'jpgs'))
        badones = [x for x in jpgs if camid in x]
        for ba in badones:
            os.remove(os.path.join(self.dir_path, 'jpgs', ba))
        fldrs = os.listdir(self.dir_path)
        badones = [x for x in fldrs if camid in x]
        for ba in badones:
            try:
                shutil.rmtree(os.path.join(self.dir_path, ba))
            except Exception:
                os.remove(os.path.join(self.dir_path, ba))
        os.remove(os.path.join(self.dir_path, 'stacks', imgname))

    def remove_image(self):
        """ Remove the selected image from disk
        """
        current_image = self.listbox.get(ACTIVE)
        if current_image == '':
            return 
        if not tkMessageBox.askyesno("Delete file", f"delete {current_image}?"):
            return
        log.info(f'removing {current_image}')
        if self.review_stack:
            self.removeRelated(current_image)
        else:
            os.remove(os.path.join(self.dir_path, current_image))
            xmlf = current_image.replace('P.jpg', '.xml')
            os.remove(os.path.join(self.dir_path, xmlf))
            self.selected[current_image] = (0,'')
        self.update_listbox(self.get_bin_list())

    def update_image(self, thing):
        """ When selected, load a new image
        """
        try:
            # Check if the list is empty. If it is, do nothing.
            if self.review_stack:
                self.current_image = os.path.join(self.dir_path, 'stacks', self.listbox.get(self.listbox.curselection()[0]))
            else:
                self.current_image = os.path.join(self.dir_path, self.listbox.get(self.listbox.curselection()[0]))
        except:
            return 0
        
        with img.open(self.current_image).resize((640,360)) as imgdata:
            thisimage = ImageTk.PhotoImage(imgdata)
            self.imagelabel.configure(image = thisimage)
            self.imagelabel.image = thisimage

        self.timestamp_label.configure(text = os.path.split(self.current_image)[1])
        return 

    def save_image(self):
        """ Marks the image as of interest
        """
        current_image = self.listbox.get(ACTIVE)
        if current_image == '':
            return 
        log.info(f'marking {current_image}')
        srcfile = createTxtFile(current_image, self.dir_path)
        _, targfile = os.path.split(srcfile)
        s3 = boto3.client('s3')
        s3.upload_file(srcfile, self.upload_bucket, f'{self.upload_folder}/{targfile}')
        cur_index = int(self.listbox.curselection()[0])
        self.listbox.itemconfig(cur_index, fg = 'green')
        self.selected[current_image] = (1, srcfile)

    def clean_folder(self):
        xmls = glob.glob(os.path.join(self.dir_path, '*.xml'))
        for xml in xmls:
            ucxml = xmltodict.parse(open(xml).read())
            fitsname = os.path.join(self.dir_path, 'jpgs', ucxml['ufocapture_record']['@cap']).replace('.fits', '.jpg')
            jpgname = xml.replace('.xml', 'P.jpg')
            try:
                os.replace(jpgname, fitsname)
            except Exception:
                pass
            os.remove(xml)
        stacklist = os.listdir(os.path.join(self.dir_path, 'stacks'))
        camlist = [x[:6] for x in stacklist if 'stack.jpg' in x]
        datalist = os.listdir(self.dir_path)
        datalist = [x for x in datalist if 'jpgs' not in x and 'mp4s' not in x and 'stacks' not in x]
        for d in datalist:
            keep = False
            for c in camlist:
                if c in d:
                    keep = True
            if keep is False:
                try:
                    os.remove(d)
                except Exception:
                    pass
        return

    def get_data(self):
        thispatt = self.newpatt.get()
        thispatt = thispatt.strip()[:14] # ignore seconds so that we don't miss data
        self.patt = thispatt         
        self.dir_path = os.path.join(self.fb_dir, thispatt)
        log.info(f'getting data matching {thispatt}')
        getLiveJpgs(thispatt, outdir=self.dir_path)
        self.update_listbox(self.get_bin_list())

    def viewWatchlist(self):
        evtfile = os.path.join(self.fb_dir,'event_watchlist.txt')
        if platform.system() == 'Darwin':       # macOS
            procid = subprocess.Popen(('open', evtfile))
        elif platform.system() == 'Windows':    # Windows
            procid = subprocess.Popen(('cmd','/c',evtfile))
        else:                                   # linux variants
            procid = subprocess.Popen(('xdg-open', evtfile))
        procid.wait()
        if not tkMessageBox.askyesno("Upload File", "Upload event watchlist?"):
            return
        else:
            self.putWatchlist()

    def getWatchlist(self):
        k = paramiko.RSAKey.from_private_key_file(os.path.expanduser(self.gmn_key))
        c = paramiko.SSHClient()
        server=self.gmn_server
        user=self.gmn_user
        log.info(f'trying {user}@{server} with {self.gmn_key}')
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname = server, username = user, pkey = k)
        scpcli = SCPClient(c.get_transport())
        log.info('getting Watchlist')
        scpcli.get('./event_watchlist.txt', self.fb_dir)
        self.viewWatchlist()

    def putWatchlist(self):
        k = paramiko.RSAKey.from_private_key_file(os.path.expanduser(self.gmn_key))
        c = paramiko.SSHClient()
        server=self.gmn_server
        user=self.gmn_user
        log.info(f'trying {user}@{server} with {self.gmn_key}')
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname = server, username = user, pkey = k)
        scpcli = SCPClient(c.get_transport())
        log.info('Uploading watchlist')
        evtfile = os.path.join(self.fb_dir,'event_watchlist.txt')
        scpcli.put(evtfile, 'event_watchlist.txt')
        self.evtMonTriggered = datetime.datetime.now() + datetime.timedelta(minutes=31)
        return 
    
    def getEventData(self):
        if self.evtMonTriggered is None:
            tkMessageBox.showinfo("Warning", 'Event Monitor has not been triggered')
            return
        if datetime.datetime.now() < self.evtMonTriggered:
            tkMessageBox.showinfo("Warning", f'Wait till {self.evtMonTriggered.strftime("%H:%M:%S")}')
            return
        os.chdir(self.fb_dir)
        evtdate = self.newpatt.get().strip()
        if len(evtdate) < 15:
            tkMessageBox.showinfo("Warning", f'Need seconds in the event date field {evtdate}')
            return
        cmd = f'../analysis/fbCollector/download_events.sh {evtdate} 1'
        log.info(f'getting data for {evtdate}')
        procid = subprocess.Popen(('bash','-c', cmd))
        procid.wait()
        tkMessageBox.showinfo("Info", 'Done')
        return 

    def getGMNData(self):
        camlist = [line for line in os.listdir(self.dir_path) if self.correct_datafile_name(line)]
        dts=[]
        camids=[]
        for cam in camlist:
            camid,_ = os.path.splitext(cam)
            spls = camid.split('_')
            if camid[:2] == 'FF':
                camids.append(spls[1])
                dts.append(camid[10:25])
            else:
                camids.append(spls[-1][:6])
                dts.append(camid[1:16])
        dts.sort()
        dtstr = f'{dts[0]}.000000'
        stationlist = ','.join(map(str, camids))
        server=self.gmn_server
        user=self.gmn_user
        log.info('getting data from GMN')
        k = paramiko.RSAKey.from_private_key_file(os.path.expanduser(self.gmn_key))
        c = paramiko.SSHClient()
        log.info(f'trying {user}@{server} with {self.gmn_key}')
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname = server, username = user, pkey = k)
        command = f'source ~/anaconda3/etc/profile.d/conda.sh && conda activate wmpl && python scripts/extract_fireball.py {dtstr} {stationlist}'
        log.info(f'running {command}')
        print(command)

        _, stdout, stderr = c.exec_command(command, timeout=900)
        for line in iter(stdout.readline, ""):
            print(line, end="")
        for line in iter(stderr.readline, ""):
            print(line, end="")
        scpcli = SCPClient(c.get_transport())
        print('done, collecting output')
        indir = os.path.join(f'event_extract/{dtstr}/')
        scpcli.get(indir, self.dir_path, recursive=True)
        command = f'rm -Rf event_extract/{dtstr}'
        log.info(f'running {command}')
        _, stdout, stderr = c.exec_command(command, timeout=120)
        for line in iter(stdout.readline, ""):
            print(line, end="")
        for line in iter(stderr.readline, ""):
            print(line, end="")
        dirs = os.listdir(os.path.join(self.dir_path, dtstr))
        for d in dirs:
            srcdir = os.path.join(self.dir_path, dtstr, d)
            targ = os.path.join(self.dir_path, d)
            os.makedirs(targ, exist_ok=True)
            for f in os.listdir(srcdir):
                shutil.copy(os.path.join(srcdir, f), targ)
        shutil.rmtree(os.path.join(self.dir_path, dtstr))
        tkMessageBox.showinfo("Data Collected", 'data collected from GMN')
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datepatt", type=str, help="date pattern to retrieve")
    args = parser.parse_args()

    dir_ = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(dir_, 'config.ini')
    noimg_file = os.path.join(dir_, 'noimage.jpg')

    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)

    log_file = os.path.join(dir_, log_timestamp() + '.log')
    handler = logging.handlers.TimedRotatingFileHandler(log_file, when='D', interval=1)  # Log to a different file each day
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(fmt='%(asctime)s-%(levelname)s-%(module)s-line:%(lineno)d - %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
    handler.setFormatter(formatter)
    log.addHandler(handler)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s-%(levelname)s: %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
    ch.setFormatter(formatter)
    log.addHandler(ch)

    # Log program start
    log.info("Program start")
    log.info('config file is {}'.format(config_file))


    # Initialize main window
    root = tk.Tk()
    root.geometry('+0+0')
    targdir = args.datepatt
    print('patt is', targdir)

    app = fbCollector(root, patt=targdir)
    root.iconbitmap(os.path.join(dir_,'ukmon.ico'))
    root.protocol('WM_DELETE_WINDOW', app.quitApplication)

    root.mainloop()
