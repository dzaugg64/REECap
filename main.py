# TODO: Créer une option "partager" pour IOS

import sys
if "pydevd" in sys.modules:
    DEBUG = True
    import logging
    logging.basicConfig(level=logging.DEBUG)
else:
    DEBUG = False

NO_OPENAI = True # Si vrai, Empêche la connexion à OPENAI

import os
import uuid
import json
import subprocess
import openai
import configparser
import redis
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sock import Sock

from audioCleaner import AudioCleaner
from feedback_server import emit_feedback, update_progressbar, close_websocket, hide_overlay

# Lecture de la configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Configuration d'OpenAI
openai.api_key = config['OPENAI']['api_key']

# Initialisation de l'AudioCleaner avec un niveau d'agressivité par défaut
audio_cleaner = AudioCleaner(aggressiveness=2)

# Configuration de l'application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FOLDER = os.path.join(BASE_DIR, 'AUDIO')
TEXT_FOLDER = os.path.join(BASE_DIR, 'TEXT')
FAKE_FOLDER = os.path.join(BASE_DIR, 'fake')
MAX_SIZE = 26214400  # 25 MB
WHISPER_COST = 0.006  # $/min
MINI_COST = 0.00000015, 0.0000006  # $/MTokens

# Création des dossiers nécessaires
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(TEXT_FOLDER, exist_ok=True)

# Initialisation de Flask et des modules associés
app = Flask(__name__)
CORS(app)  # Activer les CORS pour toutes les routes
sock = Sock(app)  # WebSocket via Flask-Sock

# Configuration de Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Route principale pour le traitement des fichiers
@app.route('/process', methods=['POST'])
def process_file():
    """Gère le téléchargement et le traitement des fichiers audio ou texte."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file"}), 400

    client_id = request.form.get('client_id')  # Récupérer le client_id transmis

    try:
        emit_feedback(redis_client, client_id,  "Téléchargement en cours...")
        update_progressbar(redis_client, client_id, "1")

        # TODO: Implémenter détection de type de fichier basée sur le contenu
        # Détecter le type de fichier
        file_ext = os.path.splitext(file.filename)[1].lower()
        unique_id = client_id + "_" + file.filename

        # Récupérer le contexte facultatif
        context = request.form.get('context', '').strip()
        print(f"Context received: {context if context else 'No context provided'}")

        # Récupère le type de document
        document_type = request.form.get('document_type', 'synthesis').strip()

        # Gère les assistants en fonction du type de document
        if document_type == 'synthesis':
            assistant_id = config['OPENAI']['synthesis_assistant_id']
            summary_filename = f"{unique_id}_synthèse.md"
        elif document_type == 'detailed-pv':
            assistant_id = config['OPENAI']['detailed_pv_assistant_id']
            summary_filename = f"{unique_id}_PV_détaillé.md"
        elif document_type == 'exec-summary':
            assistant_id = config['OPENAI']['exec_summary_assistant_id']
            summary_filename = f"{unique_id}_résumé_exécutif.md"
        else:
            return jsonify({"error": "Invalid document type"}), 400

        # Gestion des fichiers reçus
        if file_ext in ['.txt', '.md']:
            # Gestion des fichier texte
            emit_feedback(redis_client, client_id, "Début du traitement...", "Fichier texte")
            text_content = file.read().decode('utf-8')
            transcription = context + "\n\n" + text_content if context else text_content
            cost = 0.0
            duration = 0.0
            hide_overlay(redis_client, client_id)
            update_progressbar(redis_client, client_id, "60")
        else:
            # Gestion des fichiers audio
            emit_feedback(redis_client, client_id, "Début du traitement...", "Fichier audio")
            input_path = os.path.join(AUDIO_FOLDER, unique_id)
            file.save(input_path)
            hide_overlay(redis_client, client_id)
            print(f"File received and saved: {input_path}")
            update_progressbar(redis_client, client_id, "2")

            # Nettoyage de l'audio
            emit_feedback(redis_client, client_id, "Nettoyage de l'audio en cours...")
            cleaned_path = os.path.join(AUDIO_FOLDER, unique_id + "_cleaned.mp3")
            audio_cleaner.remove_silence(input_path, cleaned_path, client_id)
            print(f"Audio nettoyé et enregistré : {cleaned_path}")
            update_progressbar(redis_client, client_id, "30")

            # Conversion et découpage audio
            emit_feedback(redis_client, client_id, "Découpage de l'audio en segments...")
            duration, segments = split_audio(cleaned_path, unique_id)
            nb_segments = len(segments)
            emit_feedback(redis_client, client_id, "Découpage de l'audio en segments...", f"{nb_segments} segments créés")
            update_progressbar(redis_client, client_id, "40")

            # Transcription des segments
            if DEBUG or NO_OPENAI:
                # Use transcription from fake folder in debug mode
                fake_transcription_path = os.path.join(FAKE_FOLDER, "transcription.txt")
                with open(fake_transcription_path, "r") as fake_file:
                    transcription = fake_file.read()
                print(f"Mode debug: transcription chargée depuis {fake_transcription_path}")
                update_progressbar(redis_client, client_id, "80")
            else:
                transcriptions = []
                count = 0
                for segment in segments:
                    count += 1
                    progress = 40 + int(count / nb_segments * 40)
                    emit_feedback(redis_client, client_id, f"Transcription de {len(segments)} segments audio...",
                                  "traitement en cours... " + str(count) + "/" + str(len(segments)))
                    transcript = transcribe_audio(segment["filepath"])
                    transcriptions.append(transcript)
                    update_progressbar(redis_client, client_id, str(progress))

                # Combine les transcriptions
                transcription = " ".join(transcriptions)
                if context:
                    transcription = f"{context}\n\n{transcription}"

        # Sauve la transcription vers un fichier .txt
        transcription_filename = f"{unique_id}_transcription.txt"
        transcription_path = os.path.join(TEXT_FOLDER, transcription_filename)
        with open(transcription_path, "w") as f:
            f.write(transcription)
        print(f"Transcription complète sauvegardée : {transcription_path}")

        # Synthèse de la transcription
        emit_feedback(redis_client, client_id, "Synthèse en cours...")
        if DEBUG or NO_OPENAI:
            fake_summary_path = os.path.join(FAKE_FOLDER, "summary.md")
            with open(fake_summary_path, "r") as fake_file:
                summary = fake_file.read()
            print(f"Debug mode: Summary loaded from {fake_summary_path}")
            in_tokens, out_tokens = 0, 0  # Tokens are irrelevant in debug mode
        else:
            in_tokens, out_tokens, summary = summarize_with_meeting_synthetiser(transcription, assistant_id)
        update_progressbar(redis_client, client_id, "100")
        summary_path = os.path.join(TEXT_FOLDER, summary_filename)
        with open(summary_path, "w") as f:
            f.write(summary)
        print(f"Synthèse sauvegardée : {summary_path}")

        # Nettoyage du répertoire AUDIO et fermeture du Websocket
        cleanup_audio(client_id)
        close_websocket(redis_client, client_id)

        # Calcul du coût
        if DEBUG or NO_OPENAI:
            cost = 0.2345 # Montant aléatoire
        else:
            in_cost, out_cost = MINI_COST
            cost = duration * WHISPER_COST / 60 + in_cost * in_tokens + out_cost * out_tokens

        return jsonify({
            "cost": cost,
            "transcription_file": transcription_filename,
            "summary_file": summary_filename
        })

    except Exception as e:
        print(f"Erreur : {e}")
        emit_feedback(redis_client, client_id, f"Erreur : {str(e)}")
        cleanup_audio(client_id)
        return jsonify({"error": str(e)}), 500

@app.route('/get-file/<folder>/<filename>', methods=['GET'])
def get_file(folder, filename):
    """Serve files with proper headers and error handling."""
    try:
        valid_folders = {
            'transcriptions': TEXT_FOLDER,
            'summaries': TEXT_FOLDER
        }

        if folder not in valid_folders:
            return jsonify({"error": "Invalid folder"}), 400

        folder_path = valid_folders[folder]
        file_path = os.path.join(folder_path, filename)

        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        # Add cache control and CORS headers
        response = send_from_directory(
            folder_path,
            filename,
            as_attachment=True
        )
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Fonction pour diviser les fichiers audio
def split_audio(input_path, unique_id):
    """
    Divise un fichier MP3 en segments sans conversion.
    :param input_path: Chemin du fichier MP3 d'entrée.
    :param unique_id: Identifiant unique pour les noms de fichiers.
    :return: Durée totale et liste des segments.
    """
    cmd_duration = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
        'default=noprint_wrappers=1:nokey=1', input_path
    ]
    result = subprocess.run(cmd_duration, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    duration = float(result.stdout.decode().strip())
    print(f"Durée totale du fichier (en secondes) : {duration}")
    file_size = os.path.getsize(input_path)

    if file_size <= MAX_SIZE:
        print("Le fichier est dans les limites de taille, pas de segmentation requise.")
        segment_filename = f"{unique_id}_segment_0.mp3"
        segment_path = os.path.join(AUDIO_FOLDER, segment_filename)
        os.rename(input_path, segment_path)
        return duration, [{"filename": segment_filename, "filepath": segment_path}]

    # Diviser en segments
    nb_segments = int((file_size // MAX_SIZE) + 1)
    segment_duration = duration / nb_segments
    print(f"Nombre de segments : {nb_segments}, Durée par segment : {segment_duration} secondes")

    segment_list = []
    for i in range(nb_segments):
        start = i * segment_duration
        segment_filename = f"{unique_id}_segment_{i}.mp3"
        segment_path = os.path.join(AUDIO_FOLDER, segment_filename)

        cmd_split = [
            'ffmpeg', '-y', '-i', input_path,
            '-ss', str(start),
            '-t', str(segment_duration),
            '-c:a', 'copy',
            segment_path
        ]
        subprocess.run(cmd_split, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"Segment {i} créé : {segment_path}")
        segment_list.append({"filename": segment_filename, "filepath": segment_path})

    return duration, segment_list


# Fonction de transcription
def transcribe_audio(filepath):
    """Transcrit un fichier audio avec Whisper."""
    print(f"Transcription en cours : {filepath}")
    try:
        with open(filepath, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                file=audio_file, model="whisper-1"
            )
        print(f"Transcription completed for {filepath}: {response.text[:50]}...")
        return response.text
    except Exception as e:
        print(f"Erreur de transcription : {e}")
        raise RuntimeError(f"Erreur pendant la transcription: {e}")

# Fonction de synthèse
def summarize_with_meeting_synthetiser(transcription_text, assistant_id):
    """Génère un résumé de transcription via OpenAI."""
    print("Synthèse en cours...")
    try:
        thread = openai.beta.threads.create()
        openai.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=transcription_text
        )
        run = openai.beta.threads.runs.create_and_poll(
            assistant_id=assistant_id, thread_id=thread.id
        )
        response = openai.beta.threads.messages.list(thread_id=thread.id)
        summary = response.data[0].content[0].text.value
        in_tokens = run.usage.prompt_tokens
        out_tokens = run.usage.completion_tokens

        print(f"Document generated: {summary[:50]}...")
        print(f"Total tokens used: {in_tokens+out_tokens}")

        return in_tokens, out_tokens, summary
    except Exception as e:
        print(f"Erreur de synthèse : {e}")
        raise RuntimeError(f"Erreur : {e}")

# Nettoyage des fichiers audio
def cleanup_audio(client_id):
    """Remove all files from client_id in the audio folders."""
    for filename in os.listdir(AUDIO_FOLDER):
        if client_id in filename:
            file_path = os.path.join(AUDIO_FOLDER, filename)
            try:
                os.remove(file_path)
                print(f"Deleted segment: {file_path}")
            except Exception as e:
                print(f"Erreur lors du nettoyage {file_path}: {e}")

if __name__ == "__main__":
    if DEBUG:
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    print("Lancement du serveur Flask...")
    app.run(host='127.0.0.1', port=5000, debug=DEBUG, use_reloader=False)
