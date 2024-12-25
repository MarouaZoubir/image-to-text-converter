from django.shortcuts import render
from django.shortcuts import render
from gtts import gTTS
from django.http import HttpResponse
import os
from django.http import JsonResponse
from django.conf import settings


def index(request):
    return render(request, 'index.html')

def textToSpeech(request):
    return render(request, 'textToSpeech.html')

def convert_to_audio(request):
    if request.method == 'POST':
        text = request.POST.get('comment')
        tts = gTTS(text=text, lang='fr')
        audio_filename = 'audio_output.mp3'
        audio_path = os.path.join(settings.MEDIA_ROOT, audio_filename)
        tts.save(audio_path)
        
        # Ouvrir le fichier pour le renvoyer en réponse
        with open(audio_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="audio/mpeg")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(audio_path)
            return response
    return HttpResponse("Invalid request", status=400)
from django.http import HttpResponse
from django.shortcuts import render
import cv2
import numpy as np
import pytesseract

def image_processing(request):
    if request.method == 'POST':
        # Récupérer le fichier image à partir du formulaire
        image_file = request.FILES['image_file']
        image_data = image_file.read()
        np_data = np.frombuffer(image_data, dtype=np.uint8)

        # Lire l'image
        img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

        # Vérifier le nombre de canaux de l'image
        if len(img.shape) == 3:  # Si l'image a 3 canaux (couleur)
            # Convertir l'image en niveaux de gris
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Ajouter du bruit gaussien à l'image en niveaux de gris
            noisy_img = add_gaussian_noise(gray_img)
        elif len(img.shape) == 2:  # Si l'image est déjà en niveaux de gris
            # Ajouter du bruit gaussien à l'image en niveaux de gris
            noisy_img = add_gaussian_noise(img)
        else:
            return HttpResponse("Invalid image format")

        # Appliquer un filtre bilatéral à l'image
        bilateral = cv2.bilateralFilter(noisy_img, 45, 75, 75)

        # Appliquer CLAHE à l'image
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(bilateral)

        # Appliquer un seuillage à l'image
        ret, thresh = cv2.threshold(clahe_img, 150, 255, cv2.THRESH_BINARY)

        # Appliquer une dilatation pour améliorer les contours
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        dilation = cv2.dilate(thresh, rect_kernel, iterations=1)

        # Trouver les contours dans l'image dilatée
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Créer une copie de l'image
        im2 = img.copy()

        cnt_list = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            # Dessiner un rectangle autour du contour
            rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Extraire le texte du contour
            cropped = im2[y:y + h, x:x + w]
            text = pytesseract.image_to_string(cropped)
            cnt_list.append([x, y, text])

        # Trier la liste des contours par ordre vertical
        sorted_list = sorted(cnt_list, key=lambda x: x[1])

        # Écrire le texte extrait dans un fichier texte
        with open("recognized_text.txt", "w") as text_file:
            for x, y, text in sorted_list:
                text_file.write(text)
                text_file.write("\n")

        # Renvoyer le fichier texte en téléchargement
        with open("recognized_text.txt", "rb") as file:
            response = HttpResponse(file.read(), content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="recognized_text.txt"'
            return response
    else:
        # Si la requête n'est pas de type POST, renvoyer la page HTML
        return render(request, 'image_processing.html')

def add_gaussian_noise(image):
    row, col = image.shape
    mean = 0
    var = 0.1
    sigma = var ** 0.5
    gauss = np.random.normal(mean, sigma, (row, col))
    gauss = gauss.reshape(row, col)
    noisy = image + gauss
    return noisy.astype(np.uint8)
