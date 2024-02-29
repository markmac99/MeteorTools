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
from PIL import Image 
import requests

import boto3
import paramiko
from scp import SCPClient

from meteortools.ukmondb import getECSVs as getecsv
from wmpl.Formats.ECSV import loadECSVs
from wmpl.Formats.GenericFunctions import solveTrajectoryGeneric

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
        self.soln_outputdir = None

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

        self.shareloc = localcfg['Fireballs']['shrfldr']
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
        fileMenu.add_command(label="Archive Folder", command=self.archiveFolder)
        fileMenu.add_command(label="Delete Folder", command=self.delFolder)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.quitApplication)
        self.menuBar.add_cascade(label="File", underline=0, menu=fileMenu)

        rawMenu = Menu(self.menuBar, tearoff=0)
        rawMenu.add_command(label="Get Live Images", command=self.get_data)
        rawMenu.add_command(label="Get Videos", command=self.get_vids)
        rawMenu.add_separator()
        rawMenu.add_command(label="Get GMN Raw Data", command=self.getGMNData)
        rawMenu.add_separator()
        rawMenu.add_command(label="Get ECSVs", command=self.getECSVs)
        self.menuBar.add_cascade(label="Raw", underline=0, menu=rawMenu)

        watchMenu = Menu(self.menuBar, tearoff=0)
        watchMenu.add_command(label="Get Watchlist", command=self.getWatchlist)
        watchMenu.add_command(label="View Watchlist", command=self.viewWatchlist)
        watchMenu.add_command(label="Upload Watchlist", command=self.putWatchlist)
        watchMenu.add_separator()
        watchMenu.add_command(label="Fetch Event Data", command=self.getEventData)
        self.menuBar.add_cascade(label="Watchlist", underline=0, menu=watchMenu)

        revMenu = Menu(self.menuBar, tearoff=0)
        revMenu.add_command(label="Review Stacks", command=self.checkStacks)
        revMenu.add_command(label="Clean Folder", command=self.clean_folder)
        self.menuBar.add_cascade(label="Review", underline=0, menu=revMenu)

        solveMenu = Menu(self.menuBar, tearoff=0)
        solveMenu.add_command(label="Reduce Data", command=self.reduceCamera)
        solveMenu.add_command(label="Toggle Ignore", command=self.ignoreCamera)
        solveMenu.add_separator()
        solveMenu.add_command(label="View Raw Data", command=self.viewData)
        solveMenu.add_command(label="Upload Raw Data", command=self.uploadRaw)
        solveMenu.add_separator()
        solveMenu.add_command(label="Solve", command=self.solveOrbit)
        solveMenu.add_separator()
        solveMenu.add_command(label="View Solution", command=self.viewSolution)
        solveMenu.add_command(label="Delete Solution", command=self.removeSolution)
        solveMenu.add_separator()
        solveMenu.add_command(label="Upload Orbit", command=self.uploadOrbit)
        self.menuBar.add_cascade(label="Solve", underline=0, menu=solveMenu)
        # buttons
        self.save_panel = LabelFrame(self, text=' Image Selection ')
        self.save_panel.grid(row = 1, columnspan = 2, sticky='WE')

        self.newpatt = StringVar()
        self.newpatt.set(self.patt)

        self.patt_entry = StyledEntry(self.save_panel, textvariable = self.newpatt, width = 20)
        self.patt_entry.grid(row = 1, column = 1, columnspan = 2, sticky = "W")
        save_bmp = StyledButton(self.save_panel, text="Get Images", width = 8, command = lambda: self.get_data())
        save_bmp.grid(row = 1, column = 3)

        save_bmp = StyledButton(self.save_panel, text="Remove", width = 8, command = lambda: self.remove_image())
        save_bmp.grid(row = 1, column = 4)
        

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

    def reduceCamera(self):
        current_image = self.listbox.get(ACTIVE)
        if current_image == '':
            return 
        camid = current_image[3:9]
        print('selected camera is', camid)
        return
    
    def ignoreCamera(self):
        current_image = self.listbox.get(ACTIVE)
        if current_image == '':
            return 
        camid = current_image[3:9]
        print('selected camera is', camid)
        dirname = os.path.join(self.dir_path, camid)
        allecsvs = glob.glob(os.path.join(dirname, '*.ecsv'))
        ecsvs = [e for e in allecsvs if 'REJECT' not in e.upper()]
        rejs = [e for e in allecsvs if 'REJECT' in e.upper()]
        if len(ecsvs) == 0 and len(rejs) == 0:
            print('no files to reject or include')
            return 
        elif len(ecsvs) == 1 and len(rejs) == 0:
            os.rename(ecsvs[0], ecsvs[0].replace('.ecsv.','_REJECT.ecsv'))
            jpgname = glob.glob(self.dir_path, 'jpgs', current_image)
            os.rename(jpgname, jpgname.replace('.jpg','_REJECT.jpg'))
            return 
        elif len(ecsvs) == 0 and len(rejs) == 1:
            os.rename(ecsvs[0], ecsvs[0].replace('_REJECT.ecsv','.ecsv.'))
            jpgname = glob.glob(self.dir_path, 'jpgs', current_image)
            os.rename(jpgname, jpgname.replace('_REJECT.jpg','.jpg'))
            return 
        else:
            # more than one ECSV or REJ file to handle, urk
            print('urk')
        bin_list = [line for line in os.listdir(os.path.join(self.dir_path, 'jpgs')) if self.correct_datafile_name(line)]
        for b in bin_list:
            self.selected[b] = (0, '')
        self.update_listbox(bin_list)
        return
    
    def solveOrbit(self):
        print('Using ECSV files:')
        ecsv_names = []
        ecsv_paths = []
        for entry in sorted(os.walk(self.dir_path), key=lambda x: x[0]):
            dir_name, _, file_names = entry
            for fn in file_names:
                if fn.lower().endswith(".ecsv") and 'REJECT' not in dir_name.upper() and 'REJECT' not in fn.upper():

                    # Add ECSV file, but skip duplicates
                    if fn not in ecsv_names:
                        ecsv_paths.append(os.path.join(dir_name, fn))
                        ecsv_names.append(fn)
                        #print(fn)
        if len(ecsv_paths) < 2:
            tkMessageBox.showinfo('Warning', 'Need at least two ECSV files')
            return 
        jdt_ref, meteor_list = loadECSVs(ecsv_paths)
        mcruns = 20
        max_toffset = 5.0
        velpart = None
        vinitht = None
        plotallspatial = True
        uncertgeom = False
        jacchia = False
        traj = solveTrajectoryGeneric(jdt_ref, meteor_list, self.dir_path, 
            max_toffset=max_toffset, monte_carlo=True, mc_runs=mcruns, 
            geometric_uncert=uncertgeom, plot_all_spatial_residuals=plotallspatial, 
            show_plots=False, v_init_part=velpart, v_init_ht=vinitht, 
            show_jacchia=jacchia, enable_OSM_plot=True)
        tkMessageBox.showinfo('Info', 'Solver Finished')
        self.soln_outputdir = traj.output_dir
        return 
    
    def viewSolution(self):
        self.review_stack = False
        if not self.soln_outputdir:
            solndir = glob.glob1(self.dir_path, os.path.split(self.dir_path)[1][:8]+'*')
            if len(solndir) == 0:
                return
            solndir = os.path.join(self.dir_path, solndir[0])
            self.soln_outputdir = solndir
        bin_list = [line for line in os.listdir(self.soln_outputdir) if self.correct_datafile_name(line)]
        for b in bin_list:
            self.selected[b] = (0, '')
        self.update_listbox(bin_list)
        return 
    
    def removeSolution(self):
        if not self.soln_outputdir:
            solndir = glob.glob1(self.dir_path, os.path.split(self.dir_path)[1][:8]+'*')
            if len(solndir) == 0:
                return
            solndir = os.path.join(self.dir_path, solndir[0])
            self.soln_outputdir = solndir
        if not tkMessageBox.askyesno("Delete file", f"delete {self.soln_outputdir}?"):
            return
        shutil.rmtree(os.path.join(self.dir_path, self.soln_outputdir))
        return 
    
    def uploadOrbit(self):
        pickles=[]
        for path, _, files in os.walk(self.dir_path):
            for name in files:
                if '.pickle' in name and '_mc_' not in name:
                    pickles.append(os.path.join(path, name))

        if len(pickles) == 0:
            return
        elif len(pickles) == 1:
            pickfile = pickles[0]
        else:
            pickfile = tkFileDialog.askopenfilename(title='Select Orbit Pickle', defaultextension='*.pickle',
                                       initialdir=self.dir_path, initialfile='*.pickle',
                                       filetypes=[('pickles','*.pickle')])
        orbname = os.path.split(pickfile)[1]
        tmpdir = os.path.join(self.dir_path, 'tmpzip')
        os.makedirs(tmpdir, exist_ok=True)
        shutil.copyfile(pickfile, os.path.join(tmpdir, orbname))
        if os.path.isdir(os.path.join(self.dir_path, 'jpgs')):
            shutil.copytree(os.path.join(self.dir_path, 'jpgs'), os.path.join(tmpdir, 'jpgs'))
        if os.path.isdir(os.path.join(self.dir_path, 'mp4s')):
            shutil.copytree(os.path.join(self.dir_path, 'mp4s'), os.path.join(tmpdir, 'mp4s'))
        for path, _, files in os.walk(self.dir_path):
            for name in files:
                if '_dyn_mass_fit' in name:
                    im = Image.open(os.path.join(path, name)).convert("RGB")
                    im.save(os.path.join(tmpdir,'jpgs', name[:-4] + '.jpg'))
                    break
        zfname = os.path.join(self.dir_path, orbname[:15])
        shutil.make_archive(zfname,'zip',tmpdir)
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass
        apikey = open(os.path.expanduser('~/.ssh/fbuploadkey.txt')).readlines()[0].strip()
        headers = {'Content-type': 'application/zip', 'Slug': orbname[:15], 'apikey': apikey}
        url = f'https://api.ukmeteors.co.uk/fireballfiles?orbitfile={orbname[:15]}.zip'
        r = requests.put(url, data=open(zfname+'.zip', 'rb'), headers=headers) #, auth=('username', 'pass'))
        #print(r.text)
        if r.status_code != 200:
            tkMessageBox.showinfo('Warning', 'Problem with upload')
        else:
            tkMessageBox.showinfo('Info', 'Orbit Uploaded')
        return 
    
    def uploadRaw(self):
        zfname = os.path.join(os.getenv('TMP'), os.path.basename(self.dir_path))
        print(f'zfname is {zfname}')
        shutil.make_archive(zfname,'zip',self.dir_path)
        try:
            targname = os.path.join(self.shareloc, os.path.basename(zfname)+'.zip')
            print(f'targname is {targname}')
            shutil.copyfile(zfname+'.zip', targname)
            tkMessageBox.showinfo('Info', 'Orbit Uploaded')
        except Exception:
            tkMessageBox.showinfo('Warning', 'Problem with upload')
        return 
    
    def viewData(self):
        dirpath = self.dir_path.replace('/', '\\')
        print(f'self-dir-path {dirpath}')
        subprocess.Popen(f'explorer "{dirpath}"')
        return 
    
    def getECSVs(self):
        notgotlist=[]
        img_list = self.get_bin_list()
        for current_image in img_list:
            if not self.getOneEcsv(current_image):
                notgotlist.append(current_image)
        tkMessageBox.showinfo('Info', f'No ECSVs for {notgotlist}')
        return
    
    def getOneEcsv(self, current_image):
        if current_image[:1] == 'M':
            datestr = current_image[1:16]
            statid = current_image[-11:-5]
        elif current_image[:2] == 'FF':
            statid = current_image[3:9]
            datestr = current_image[10:25]
        else:
            return
        dtval = datetime.datetime.strptime(datestr, '%Y%m%d_%H%M%S')
        datestr = dtval.strftime('%Y-%m-%dT%H:%M:%S')
        try:
            lis = getecsv(statid, datestr, savefiles=True, outdir=os.path.join(self.dir_path, statid))
            for li in lis:
                if 'issue getting data' in li:
                    return False
            return True
        except Exception:
            return False

    def get_bin_list(self):
        """ Get a list of image files in a given directory.
        """
        if self.dir_path is None:
            dirname = tkFileDialog.askdirectory(parent=root,initialdir=self.fb_dir,
                title='Please select a directory')    
            _, thispatt = os.path.split(dirname)
            #print(dirname, thispatt)
            self.dir_path = dirname
            self.patt = thispatt
            self.newpatt.set(self.patt)

        if self.review_stack is False:
            targdir = os.path.join(self.dir_path, 'jpgs')
        else:
            targdir = os.path.join(self.dir_path, 'stacks')
        #print(targdir)
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
            #print(line, self.selected[line])
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
        self.soln_outputdir = None
        bin_list = self.get_bin_list()
        for b in bin_list:
            self.selected[b] = (0, '')
        self.update_listbox(bin_list)

    def archiveFolder(self):
        noimgdata = img.open(noimg_file).resize((640,360))
        noimage = ImageTk.PhotoImage(noimgdata)
        self.imagelabel.configure(image = noimage)
        self.imagelabel.image = noimage
        if self.dir_path is not None and self.dir_path != self.fb_dir:
            try:
                _, fldr = os.path.split(os.path.normpath(self.dir_path))
                yr = fldr[:4]
                archdir = os.path.join(self.fb_dir, yr)
                os.makedirs(archdir, exist_ok=True)
                zfname = os.path.join(archdir, fldr)
                shutil.make_archive(zfname,'zip',self.fb_dir, fldr)
                shutil.rmtree(self.dir_path)
                self.dir_path = self.fb_dir
            except Exception as e:
                print(f'unable to archive {self.dir_path}')
                print(e)

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
        if ('.jpg' in line or '.png' in line) and 'noimage' not in line:
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
            try:
                os.remove(os.path.join(self.dir_path, 'jpgs', current_image))
            except Exception:
                pass
            xmlf = current_image.replace('P.jpg', '.xml')
            try:
                os.remove(os.path.join(self.dir_path, 'jpgs', xmlf))
            except Exception:
                pass
            self.selected[current_image] = (0,'')
        self.update_listbox(self.get_bin_list())

    def update_image(self, thing):
        """ When selected, load a new image
        """
        try:
            # Check if the list is empty. If it is, do nothing.
            if self.review_stack:
                self.current_image = os.path.join(self.dir_path, 'stacks', self.listbox.get(self.listbox.curselection()[0]))
            elif self.soln_outputdir:
                self.current_image = os.path.join(self.soln_outputdir, self.listbox.get(self.listbox.curselection()[0]))
            else:
                self.current_image = os.path.join(self.dir_path, 'jpgs', self.listbox.get(self.listbox.curselection()[0]))
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
        self.patt = thispatt.ljust(15,'0')
        self.dir_path = os.path.join(self.fb_dir, self.newpatt.get())
        log.info(f'getting data matching {thispatt}')
        os.makedirs(os.path.join(self.dir_path, 'jpgs'), exist_ok=True)
        reqdate = datetime.datetime.strptime(self.patt, '%Y%m%d_%H%M%S')
        reqdate = reqdate + datetime.timedelta(seconds=-30)
        getLiveJpgs(reqdate.strftime('%Y%m%d_%H%M%S'), outdir=os.path.join(self.dir_path, 'jpgs'))
        self.renameImages(self.dir_path)
        self.update_listbox(self.get_bin_list())

    def get_vids(self):
        jpglist = glob.glob1(os.path.join(self.dir_path,'jpgs'), 'FF*.jpg')
        os.makedirs(os.path.join(self.dir_path, 'mp4s'), exist_ok=True)
        count = 0
        for jpg in jpglist:
            mp4 = jpg.replace('.jpg','.mp4')
            ym = mp4[10:16]
            url = f'https://archive.ukmeteors.co.uk/img/mp4/{ym[:4]}/{ym}/{mp4}'
            get_response = requests.get(url, stream=True)
            if get_response.status_code == 200:
                print(f'retrieved {mp4}')
                count += 1
                with open(os.path.join(self.dir_path, 'mp4s', mp4), 'wb') as f:
                    for chunk in get_response.iter_content(chunk_size=4096):
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)
        print(f'retrieved {count} videos')
        tkMessageBox.showinfo("Info", f'Retrieved {count} videos')
        return 

    def renameImages(self, dir_path):
        xmllist = glob.glob(os.path.join(dir_path,'jpgs', 'M*.xml'))
        for xmlf in xmllist:
            jpgf = xmlf.replace('.xml','P.jpg')
            if os.path.isfile(jpgf):
                xmld = xmltodict.parse(open(xmlf).read())
                realfname = xmld['ufocapture_record']['@cap'].replace('.fits','.jpg')
                if not os.path.isfile(os.path.join(dir_path, 'jpgs', realfname)):
                    os.rename(jpgf, os.path.join(dir_path, 'jpgs', realfname))
                else:
                    os.remove(jpgf)
                os.remove(xmlf)
        return 

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
        self.evtMonTriggered = datetime.datetime.now() + datetime.timedelta(minutes=10)
        return 
    
    def getEventData(self):
        if self.evtMonTriggered is None:
            tkMessageBox.showinfo("Warning", 'Event Monitor has not been triggered')
            return
        if datetime.datetime.now() < self.evtMonTriggered:
            tkMessageBox.showinfo("Warning", f'Wait till at least {self.evtMonTriggered.strftime("%H:%M:%S")}')
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
    root.iconbitmap(os.path.join(dir_,'ukmda.ico'))
    root.protocol('WM_DELETE_WINDOW', app.quitApplication)

    root.mainloop()
