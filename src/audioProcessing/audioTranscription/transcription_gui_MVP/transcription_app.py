from src.audioProcessing.audioTranscription.transcription_gui_MVP.transcription_gui.view_transcription_GUI import ViewTranscriptionApp


if __name__ == "__main__":
    # root = tk.Tk()

    # Specify a default folder or leave it as None to prompt the user
    default_folder = "/Users/vtn/pythonProjects/audioVIdeo/testTensorFlowM1/out/audio/transcription"

    app = ViewTranscriptionApp(default_folder)
    app.update_gui()

