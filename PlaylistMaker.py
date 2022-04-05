try:
    import tkinter as tk, tkinter.font
    from tkinter import ttk
    from tkinter import filedialog
    import os, re, os.path
    from tkinter.messagebox import showinfo, showwarning, showerror
    import mutagen as tmnt
except ImportError as e:
    showerror('Error', e)
    exit()

#global vars
formats = ('.flac', '.m4a', '.mp3', '.ogg', '.wav', '.wma')
path = ''
previous_path = ''
subfolder = ''
audio_list = []

#create root window    
root = tk.Tk()
name = "M3U Playlist Maker v1.0"
root.title(name)
win_width = 600
win_height = 445

# get screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# find center point
center_x = int(screen_width/2 - win_width/2)
center_y = int(screen_height/2 - win_height/2)
root.geometry(f'{win_width}x{win_height}+{center_x}+{center_y}')
root.resizable(False, False)

pWhite = tk.PhotoImage(file='pics/asset_white50x_transparent.png')
pBlack = tk.PhotoImage(file='pics/asset_black50x_transparent.png')
pIcon = tk.PhotoImage(file='pics/asset_white50x.png')
root.iconphoto(False, pIcon)
font = tkinter.font.nametofont('TkDefaultFont')

#playlist name
playlist_name_mode = tk.StringVar()
playlist_name_mode.set('automatic')
playlist_name = tk.StringVar()


def ask_directory():
    global path
    path = filedialog.askdirectory()
    fill_audio_list()


def audio_length(audio):
    try:
        audio1 = tmnt.File(path+'/'+audio)
        audio_info = audio1.info
        return '-1' if (int(audio_info.length)==0) else str(int(audio_info.length))
    except Exception as e:
        return '-1'


def show_created_info(m3uType):
    showinfo(name,
                    'Playlist created: '+path+'/'+playlist_name.get()+m3uType)


def create_playlist():
    if (len(audio_list)==0):
        showwarning(name, 'No folder selected')
    else:
        if (playlist_name_mode.get() == 'custom'):
            if(len(playlist_name.get()) == 0):
                entry.state(['invalid'])
                showwarning(name, 'Playlist name cannot be empty')
                entry.state(['!invalid'])
                entry.focus()
                return
            if('.m3u' in playlist_name.get()):
                a = playlist_name.get()
                a = a.replace('.m3u', '')
                playlist_name.set(a)
        else:
            playlist_name.set(subfolder)
        try:
            with open(path+'/'+playlist_name.get()+'.m3u', 'w') as playlist:
                playlist.write('#EXTM3U'+'\n')            
                for audio in audio_list:
                    length = audio_length(audio)
                    playlist.write('#EXTINF:'+length+','+audio+'\n')
                    playlist.write('../'+subfolder+'/'+audio+'\n')
            show_created_info('.m3u')
        except UnicodeEncodeError:
            #deleting failed playlist
            if (os.path.isfile(path+'/'+playlist_name.get()+'.m3u')):
                os.remove(path+'/'+playlist_name.get()+'.m3u')
                
            #attempting to create m3u8 playlist
            with open(path+'/'+playlist_name.get()+'.m3u8', 'w', encoding='utf-8') as playlist:
                playlist.write('#EXTM3U'+'\n')            
                for audio in audio_list:
                    length = audio_length(audio)
                    playlist.write('#EXTINF:'+length+','+audio+'\n')
                    playlist.write('../'+subfolder+'/'+audio+'\n')
            show_created_info('.m3u8')
        except Exception as e:
            showerror('Error: ', e)


def set_entry():
    if(playlist_name_mode.get() == 'custom'):
        entry.configure(state='normal')
        entry.focus()
    else:
        entry.configure(state='disabled')


def insert_to_text_widget(song_list):
    # inserting files from folder to text widget
    text.configure(state='normal')
    text.delete('1.0', tk.END)
    line = 1
    for song in song_list:
        if song == song_list[-1]:
            text.insert(f'{line}.0', song)
            break
        text.insert(f'{line}.0', song+'\n')
        line += 1
    text.configure(state='disabled')
    image_label.configure(image=pWhite)


def natural_sort(list):
    def convert(text): return int(text) if text.isdigit() else text
    def natural_key(key): return [convert(c) for c in re.split(r'(\d+)', key)]
    list.sort(key=natural_key)
    return list


def fill_audio_list():
    global audio_list
    song_list = []
    if (len(path) > 0):
        global subfolder
        subfolder = os.path.basename(path)
        file_list = os.listdir(path)
        for file in file_list:
            if (any(format in file for format in formats)):
                song_list.append(file)
    song_list = natural_sort(song_list)
    if (len(song_list) == 0): # no supported files in dir
        return 'no_audio'
    audio_list = song_list
    insert_to_text_widget(song_list)


def select_folder_button():
    global path
    global previous_path
    path = filedialog.askdirectory()
    var = fill_audio_list()
    if (var == 'no_audio'):
        if (len(path) == 0):
            path = previous_path
        else:
            showwarning(name, 'No supported files in '+path)
            #wipe list and textbox
            global audio_list
            audio_list.clear()
            text.configure(state='normal')
            text.delete('1.0', tk.END)
            text.configure(state='disabled')
            image_label.configure(image=pBlack)
    else: 
        previous_path = path


# label image with info text
textInfo = '    To make a playlist select a folder with audio files and click on create playlist button.'
textInfo += '\n    Supported formats: '
for format in formats:
    if format == formats[-1]:
        textInfo += format.replace('.', '').upper() + '.'
        break
    textInfo += format.replace('.', '').upper() + ', '
image_label = tk.Label(
    root,
    image=pBlack,
    text=textInfo,
    compound='left',
    justify='left')
image_label.grid(column=0, row=0, sticky='W', padx=10, pady=5)

# slect folder button
sel_folder_btn = ttk.Button(
    root,
    text='Select folder',
    command=select_folder_button,
    takefocus=False)
sel_folder_btn.grid(column=0, row=1, sticky='W', padx=15)

# frames
frame = tk.Frame(root, width=580, height=200, highlightbackground='gray80', highlightthickness=1)
frame.grid(column=0, row=2, padx=10, pady=10)
frame.pack_propagate(False)
frame2 = tk.Frame(frame, width=556, height=200)
frame2.pack(side='left')
frame2.pack_propagate(False)
frame3 = tk.Frame(frame, width=24, height=200, background='white')
frame3.pack(side='right')
frame3.pack_propagate(False)
frame_entry = tk.Frame(root, width=388, height=25, background='yellow')
frame_entry.place(x=200, y=365)
frame_entry.pack_propagate(False)

# textbox
text = tk.Text(
    frame2,
    state='disabled', borderwidth=0)
text.pack(expand=True, fill='both')

# scrollbar
scrollbar = ttk.Scrollbar(
    frame3,
    orient='vertical',
    command=text.yview)
scrollbar.pack(expand=True, fill='y')
text['yscrollcommand'] = scrollbar.set

# labela
label = tk.Label(
    root,
    text="Playlist name:")
label.grid(column=0, row=4, sticky='W', padx=15)

# radiobuttons
texts = ('Same as folder', 'Custom name')
values = ('automatic', 'custom')
row = 5
for i in range(2):
    rb = ttk.Radiobutton(
        root,
        text=texts[i],
        value=values[i],
        variable=playlist_name_mode,
        command=set_entry,
        takefocus=False)
    rb.grid(column=0, row=row, sticky='W', padx=50, pady=5)
    row += 1

# entry
entry = ttk.Entry(
    frame_entry,
    textvariable=playlist_name,
    state='disabled')
entry.pack(expand=True, fill='both')

# create playlist button
make_m3u_btn = ttk.Button(
    root,
    text='Create playlist',
    command=create_playlist,
    takefocus=False)
make_m3u_btn.grid(column=0, row=7, sticky='W', padx=15, pady=10)

# display
root.mainloop()
