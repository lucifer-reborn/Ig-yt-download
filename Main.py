# ===================== IMPORTS =====================
import os, sys, time, threading, shutil, subprocess, contextlib
from urllib.parse import urlparse, urlunparse
from shutil import get_terminal_size
import instaloader
import yt_dlp

GREEN = "\033[38;2;0;255;0m"
RESET = "\033[0m"

ASCII_ART = [
" ██▓    █    ██  ▄████▄   ██   █████▓█████ ██▀███  ",
"▓██▒    ██  ▓██▒▒██▀ ▀█ ▒▓██ ▓██    ▓█   ▀▓██ ▒ ██▒",
"▒██░   ▓██  ▒██░▒▓█    ▄░▒██ ▒████  ▒███  ▓██ ░▄█ ▒",
"▒██░   ▓▓█  ░██░▒▓▓▄ ▄██ ░██ ░▓█▒   ▒▓█  ▄▒██▀▀█▄  ",
"░██████▒▒█████▓ ▒ ▓███▀  ░██▒░▒█░   ░▒████░██▓ ▒██▒",
"░ ▒░▓   ▒▓▒ ▒ ▒ ░ ░▒ ▒   ░▓ ░ ▒ ░   ░░ ▒░ ░ ▒▓ ░▒▓░",
"░ ░ ▒   ░▒░ ░ ░   ░  ▒    ▒ ░ ░      ░ ░    ░▒ ░ ▒░",
"  ░ ░    ░░ ░ ░ ░         ▒   ░ ░      ░     ░   ░ ",
"    ░     ░     ░ ░       ░ ░          ░     ░     "
]

BASE="BY-LUCIFER"
TEMP="__tmp__"

def clear(): os.system("cls" if os.name=="nt" else "clear")
def center(t): return " "*max((get_terminal_size().columns-len(t))//2,0)+t
def print_art():
    for l in ASCII_ART: print(GREEN+center(l)+RESET)

def folders():
    for p in [
        f"{BASE}/YOUTUBE/AUDIO", f"{BASE}/YOUTUBE/VIDEO",
        f"{BASE}/INSTAGRAM/AUDIO", f"{BASE}/INSTAGRAM/VIDEO",
        f"{BASE}/INSTAGRAM/POST"]:
        os.makedirs(p,exist_ok=True)

@contextlib.contextmanager
def suppress_output():
    with open(os.devnull,"w") as d:
        o,e=sys.stdout,sys.stderr
        sys.stdout=sys.stderr=d
        try: yield
        finally: sys.stdout,sys.stderr=o,e

def spinner(stop):
    s="|/-\\"
    i=0
    while not stop.is_set():
        print(f"\r{GREEN}Processing may take some time... {s[i%4]}{RESET}",end="",flush=True)
        i+=1; time.sleep(0.1)
    print("\r"+" "*40+"\r",end="")

class SilentLogger:
    def debug(self,msg): pass
    def warning(self,msg): pass
    def error(self,msg): pass

def fix_yt(u):
    p=urlparse(u)
    if "/shorts/" in p.path:
        return f"https://www.youtube.com/watch?v={p.path.split('/shorts/')[-1]}"
    return urlunparse((p.scheme,p.netloc,p.path,'','',''))

def youtube(url,opt):
    stop=threading.Event()
    threading.Thread(target=spinner,args=(stop,)).start()
    try:
        ydl={"quiet":True,"logger":SilentLogger()}
        if opt=="1":
            ydl.update({
                "format":"bestaudio",
                "outtmpl":f"{BASE}/YOUTUBE/AUDIO/%(title)s.%(ext)s",
                "postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"mp3"}]})
        else:
            ydl.update({
                "format":"bestvideo+bestaudio/best",
                "outtmpl":f"{BASE}/YOUTUBE/VIDEO/%(title)s.%(ext)s",
                "postprocessors":[{"key":"FFmpegVideoConvertor","preferedformat":"mp4"}]})
        with yt_dlp.YoutubeDL(ydl) as y:
            y.download([fix_yt(url)])
        stop.set()
        print(GREEN+("Audio" if opt=="1" else "Video")+" successfully saved"+RESET)
    except:
        stop.set()
        print(GREEN+"Failed"+RESET)

def shortcode(u): return urlparse(u).path.rstrip("/").split("/")[-1]

def extract_audio(v,a):
    subprocess.run(["ffmpeg","-y","-i",v,"-vn","-ab","192k",a],
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def instagram(url,opt):
    stop=threading.Event()
    threading.Thread(target=spinner,args=(stop,)).start()
    shutil.rmtree(TEMP,ignore_errors=True); os.makedirs(TEMP)
    try:
        with suppress_output():
            L=instaloader.Instaloader(
                download_pictures=True,download_videos=True,
                save_metadata=False,compress_json=False,quiet=True)
            p=instaloader.Post.from_shortcode(L.context,shortcode(url))
            L.download_post(p,TEMP)
        for f in os.listdir(TEMP):
            s=os.path.join(TEMP,f)
            if f.endswith((".jpg",".png")) and opt=="3":
                shutil.move(s,f"{BASE}/INSTAGRAM/POST/post{len(os.listdir(f'{BASE}/INSTAGRAM/POST'))+1}.jpg")
            elif f.endswith(".mp4"):
                if opt=="2":
                    shutil.move(s,f"{BASE}/INSTAGRAM/VIDEO/reel{len(os.listdir(f'{BASE}/INSTAGRAM/VIDEO'))+1}.mp4")
                elif opt=="1":
                    a=f"{BASE}/INSTAGRAM/AUDIO/audio{len(os.listdir(f'{BASE}/INSTAGRAM/AUDIO'))+1}.mp3"
                    extract_audio(s,a); os.remove(s)
        stop.set()
        print(GREEN+["","Audio","Reel","Post"][int(opt)]+" successfully saved"+RESET)
    except:
        stop.set()
        print(GREEN+"Failed"+RESET)
    shutil.rmtree(TEMP,ignore_errors=True)

def main():
    folders()
    while True:
        clear(); print_art()
        print(GREEN+center("(1) YouTube    (2) Instagram    (0) Exit")+RESET)
        c=input("Select option: ").strip()

        if c=="1":
            while True:
                clear(); print_art()
                print(GREEN+center("(1) Audio    (2) Video    (0) Back")+RESET)
                o=input("Select option: ").strip()
                if o=="0": break
                youtube(input("Enter link: ").strip(),o)
                input("Press Enter to continue...")

        elif c=="2":
            while True:
                clear(); print_art()
                print(GREEN+center("(1) Audio    (2) Reel    (3) Post    (0) Back")+RESET)
                o=input("Select option: ").strip()
                if o=="0": break
                instagram(input("Enter link: ").strip(),o)
                input("Press Enter to continue...")

        elif c=="0":
            sys.exit()

if __name__=="__main__":
    main()
