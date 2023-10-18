import h5py
import numpy as np

class EmbeddingsHDF5Handler:
    def __init__(self, hdf5_file):
        self.hdf5_file = hdf5_file
        self.embeddings_data = None  # Store embeddings data in memory

        # Load embeddings into memory
        self.load_embeddings_into_memory()

    def load_embeddings_into_memory(self):
        with h5py.File(self.hdf5_file, "r") as hf:
            self.embeddings_data = {}
            for speaker in hf:
                self.embeddings_data[speaker] = hf[speaker]["embeddings"][:]

    def write_embeddings(self, embeddings_list, speaker_names):
        with h5py.File(self.hdf5_file, "a") as hf:  # Use 'a' for append mode
            for i, speaker in enumerate(speaker_names):
                if speaker in hf:
                    existing_embeddings = self.embeddings_data[speaker]
                    updated_embeddings = np.vstack((existing_embeddings, embeddings_list[i]))
                    hf[speaker]["embeddings"][:] = updated_embeddings
                    # Update embeddings in memory
                    self.embeddings_data[speaker] = updated_embeddings
                else:
                    speaker_group = hf.create_group(speaker)
                    speaker_group.create_dataset("embeddings", data=embeddings_list[i])
                    # Store embeddings in memory for the new speaker
                    self.embeddings_data[speaker] = embeddings_list[i]

    # Other methods remain unchanged
if __name__ == "__main__":

    # Example usage
    hdf5_file_path = "embeddings.hdf5"

    # Load embeddings into memory for faster lookup
    embeddings_handler = EmbeddingsHDF5Handler(hdf5_file_path)

    # Perform speaker identification or retrieval using the loaded embeddings
    # ...
