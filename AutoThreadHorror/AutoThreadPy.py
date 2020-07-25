import praw
import pyttsx3
from googletrans import Translator
import os
from pydub import AudioSegment
from moviepy.editor import *

#Recupère l'histoire directement depuis le subreddit : Let's Not Meet
def getpoststory():
    #Récupère l'histoire sur reddit
    title_of_story = ""
    urlofstory = ""
    authorofstory = ""
    reddit = praw.Reddit(client_id='YOUR CLIENT ID', \
                     client_secret='YOUR SECRET CLIENT ID', \
                     user_agent='THE NAME OF USER AGENT', \
                     )
    subreddit = reddit.subreddit('LetsNotMeet')
    hot_subreddit = subreddit.hot(limit = 3)
    storytext = ""
    for submission in hot_subreddit:
        if not submission.stickied:
            storytext = submission.selftext
            title_of_story = submission.title
            urlofstory = submission.url
            authorofstory = submission.author
    #On sépare le texte qui est trop long pour la traduction
    storytextlist = storytext.split(".")

    for i in range(0,len(storytextlist)):
        storytextlist[i] = storytextlist[i].replace('**', '')
        storytextlist[i] = storytextlist[i].replace('24/24','24 hours a day')
        storytextlist[i] = storytextlist[i].replace('\n','') + "."



    return storytextlist, title_of_story, urlofstory, authorofstory

#"Lit" l'histoire et enregistre les fichiers audio dans un dossier
def historytospeech(textstoryliste, wantfrench):
    #Efface les anciens fichiers audio
    listemp3fichiers = os.listdir('AudioParts/')
    for fichier in listemp3fichiers :
        os.remove('AudioParts/'+fichier)
    #Crée les fichiers audio
    engine = pyttsx3.init()

    if (wantfrench)  :
        engine.setProperty("voice", id_frenchVoice)
    else :
        engine.setProperty("voice", id_englishVoice)

    for i in range(0,len(textstoryliste)):
        engine.save_to_file(textstoryliste[i], 'AudioParts/textstorypart' + str(i) +'.wav')
        engine.runAndWait()

#Traduit le texte (qui de base est en anglais)
def translateText(textstoryliste):
    translator = Translator()
    for i in range(0, len(textstoryliste)):
        textstoryliste[i] = translator.translate(textstoryliste[i], dest="fr").text
    return textstoryliste

#Assemble les mp3 pour la vidéo
def mp3ASSEMBLE():
    listemp3fichiers = TriageEZ(os.listdir('AudioParts/'))

    combined = AudioSegment.empty()
    for filemp3 in listemp3fichiers :
        combined += AudioSegment.from_wav('AudioParts/' + filemp3)
    combined.export("Finalsound.wav", format="wav")

#Permet de trier dans l'ordre les fichiers mp3
def TriageEZ(listefilesmp3) :
    newlistesorted = []
    for i in range(0, len(listefilesmp3)):
        for file in listefilesmp3 :
            numbersound = ""
            for lettre in file:
                if str(lettre) in "0123456789" :
                    numbersound += str(lettre)
            if str(numbersound) == str(i) :
                newlistesorted.append(file)
    return newlistesorted

#Crée la vidéo finale (quick version)
def CreateVideo(finalmp3filename, overlayname, imagetoadd, titlevideo) :
    #Set up the Audio
    audioclip = AudioFileClip(finalmp3filename)
    new_audioclip = CompositeAudioClip([audioclip,audioclip])

    #Set up the overlay
    OverImg = ImageClip(overlayname).set_duration(new_audioclip.duration)
    OverImg = OverImg.resize(height=720)

    #Set up the background img
    background = ImageClip(imagetoadd).set_duration(new_audioclip.duration)
    background = background.resize((1280,720))

    #using color key to remove green background

    masked_overlay = OverImg.fx(vfx.mask_color, color = [0,255,0], thr=100, s=5)
    masked_overlay = masked_overlay.set_duration(new_audioclip.duration)

    #Creates the final clip
    final_clip = CompositeVideoClip([
        background,
        masked_overlay
    ]).set_duration(new_audioclip.duration)

    final_clip = vfx.blackwhite(final_clip)
    final_clip.audio = new_audioclip
    final_clip.write_videofile("Videosthread/" + str(titlevideo) + ".mp4", fps=1)

def CreateTextfileCredits(author, title, url):
    with open("Creditsofvideos/" + str(title) + ".txt", "w") as file :
        file.write("author : " + str(author) + "\n")
        file.write("url : " + str(url) + "\n")
        file.write("title of the story : " + str(title) + "\n")

#Choose the language of the video
want_french_video = False

#Put here the path of the voices (for pyttsx3)

id_frenchVoice = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_FR-FR_HORTENSE_11.0"
id_englishVoice = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"

if __name__ == "__main__" :
    if (want_french_video == True) :
        poststory, title_of_story, urlofstory, authorofstory = getpoststory()
        print("Title : ", title_of_story)
        print("Url : ", urlofstory)
        print("Author: ", authorofstory)
        finaltext = translateText(poststory)
        historytospeech(finaltext, want_french_video)
        mp3ASSEMBLE()
        CreateVideo("Finalsound.wav", 'OverlayThreadImg.jpg', "backgroundimg.jpg", title_of_story)
        CreateTextfileCredits(authorofstory, title_of_story, urlofstory)
    else :
        poststory, title_of_story, urlofstory, authorofstory = getpoststory()
        print("Title : ", title_of_story)
        print("Url : ", urlofstory)
        print("Author: ", authorofstory)
        finaltext = poststory
        historytospeech(finaltext, want_french_video)
        mp3ASSEMBLE()
        CreateVideo("Finalsound.wav", 'OverlayThreadImg.jpg', "backgroundimg.jpg", title_of_story)
        CreateTextfileCredits(authorofstory, title_of_story, urlofstory)

