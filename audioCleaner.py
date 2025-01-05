import wave
import webrtcvad
import contextlib
import subprocess
import os
from feedbacks import emit_feedback, update_progressbar

# Configuration de l'application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FOLDER = os.path.join(BASE_DIR, 'AUDIO')

class AudioCleaner:
    def __init__(self, aggressiveness=1):
        """
        Initialise le nettoyeur audio avec un niveau d'agressivité.
        :param aggressiveness: Niveau d'agressivité du VAD (0-3, 3 étant le plus agressif).
        """
        if not (0 <= aggressiveness <= 3):
            raise ValueError("L'agressivité doit être entre 0 et 3.")
        self.vad = webrtcvad.Vad(aggressiveness)

    def _read_wave(self, path):
        """
        Lit un fichier WAV mono et retourne ses données PCM et son taux d'échantillonnage.
        :param path: Chemin du fichier WAV.
        :return: Tuple (pcm_data, sample_rate).
        """
        with contextlib.closing(wave.open(path, 'rb')) as wf:
            num_channels = wf.getnchannels()
            if num_channels != 1:
                raise ValueError("Le fichier audio doit être mono.")
            sample_width = wf.getsampwidth()
            if sample_width != 2:
                raise ValueError("Le fichier audio doit avoir une largeur d'échantillon de 16 bits.")
            sample_rate = wf.getframerate()
            pcm_data = wf.readframes(wf.getnframes())
            return pcm_data, sample_rate

    def _write_wave(self, path, audio, sample_rate):
        """
        Écrit des données PCM dans un fichier WAV.
        :param path: Chemin de sortie pour le fichier WAV.
        :param audio: Données PCM.
        :param sample_rate: Taux d'échantillonnage.
        """
        with contextlib.closing(wave.open(path, 'wb')) as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio)

    def _convert_to_wav(self, input_path, output_path):
        """
        Convertit un fichier audio en WAV mono avec un échantillonnage de 16 kHz.
        :param input_path: Chemin du fichier d'entrée.
        :param output_path: Chemin du fichier WAV de sortie.
        """
        subprocess.run([
            "ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", "-f", "wav", output_path
        ], check=True)

    def _convert_to_mp3(self, input_path, output_path):
        """
        Convertit un fichier audio en MP3 avec un débit binaire de 64 kbps.
        :param input_path: Chemin du fichier d'entrée.
        :param output_path: Chemin du fichier MP3 de sortie.
        """
        subprocess.run([
            "ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", "-b:a", "64k", output_path
        ], check=True)

    def remove_silence(self, input_path, output_path, client_id):
        """
        Supprime les silences d'un fichier audio et génère un fichier MP3 nettoyé.
        :param input_path: Chemin du fichier d'entrée (audio brut).
        :param output_path: Chemin du fichier MP3 de sortie nettoyé.
        """
        intermediate_wav = os.path.join(AUDIO_FOLDER,"intermediate.wav")
        cleaned_wav = os.path.join(AUDIO_FOLDER,"cleaned.wav")

        try:
            # Convertir en WAV intermédiaire
            emit_feedback(client_id, "Nettoyage de l'audio en cours...", "Conversion en wav")
            self._convert_to_wav(input_path, intermediate_wav)
            update_progressbar(client_id, 10)

            # Nettoyer les silences
            emit_feedback(client_id, "Nettoyage de l'audio en cours...", "Suppression des silences")
            pcm_data, sample_rate = self._read_wave(intermediate_wav)

            frame_duration = 30  # Durée des trames en ms
            frame_size = int(sample_rate * frame_duration / 1000 * 2)
            frames = [pcm_data[i:i + frame_size] for i in range(0, len(pcm_data), frame_size)]

            segments = []
            for frame in frames:
                if len(frame) == frame_size and self.vad.is_speech(frame, sample_rate):
                    segments.append(frame)

            non_silent_audio = b''.join(segments)
            self._write_wave(cleaned_wav, non_silent_audio, sample_rate)
            update_progressbar(client_id, 20)

            # Convertir en MP3 final
            emit_feedback(client_id, "Nettoyage de l'audio en cours...", "Conversion en mp3")
            self._convert_to_mp3(cleaned_wav, output_path)

        finally:
            # Suppression des fichiers intermédiaires
            if os.path.exists(intermediate_wav):
                os.remove(intermediate_wav)
            if os.path.exists(cleaned_wav):
                os.remove(cleaned_wav)

# Exemple d'utilisation
if __name__ == "__main__":
    cleaner = AudioCleaner(aggressiveness=1)

    input_audio = "/opt/reecap/test_audio.m4a"
    output_audio = "/home/dzaugg/reecap/test1.mp3"

    cleaner.remove_silence(input_audio, output_audio)
    print(f"Fichier nettoyé enregistré sous : {output_audio}")

    cleaner = AudioCleaner(aggressiveness=2)

    input_audio = "/opt/reecap/test_audio.m4a"
    output_audio = "/home/dzaugg/reecap/test2.mp3"

    cleaner.remove_silence(input_audio, output_audio)
    print(f"Fichier nettoyé enregistré sous : {output_audio}")

    cleaner = AudioCleaner(aggressiveness=3)

    input_audio = "/opt/reecap/test_audio.m4a"
    output_audio = "/home/dzaugg/reecap//test3.mp3"

    cleaner.remove_silence(input_audio, output_audio)
    print(f"Fichier nettoyé enregistré sous : {output_audio}")
