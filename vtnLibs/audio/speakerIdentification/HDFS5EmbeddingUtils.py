import h5py
import numpy as np

class EmbeddingsHDF5Handler:
    def __init__(self, hdf5_file):
        self.hdf5_file = hdf5_file

    def write_embeddings(self, embeddings_list, speaker_names):
        with h5py.File(self.hdf5_file, "w") as hf:
            for i, speaker in enumerate(speaker_names):
                speaker_group = hf.create_group(speaker)
                speaker_group.create_dataset("embeddings", data=embeddings_list[i])

    def write_embeddings(self, embeddings_list, speaker_names):
        with h5py.File(self.hdf5_file, "a") as hf:  # Use 'a' for append mode
            for i, speaker in enumerate(speaker_names):
                if speaker in hf:
                    # If the speaker already exists, append the new embeddings
                    existing_embeddings = hf[speaker]["embeddings"][:]
                    updated_embeddings = np.vstack((existing_embeddings, embeddings_list[i]))
                    hf[speaker]["embeddings"][:] = updated_embeddings
                else:
                    # If the speaker is new, create a new group and store the embeddings
                    speaker_group = hf.create_group(speaker)
                    speaker_group.create_dataset("embeddings", data=embeddings_list[i])

    def read_embeddings(self):
        embeddings = []
        speaker_names = []

        with h5py.File(self.hdf5_file, "r") as hf:
            for speaker in hf:
                speaker_group = hf[speaker]
                embeddings.append(speaker_group["embeddings"][:])
                speaker_names.append(speaker)

        return embeddings, speaker_names

    def get_embeddings_for_speaker(self, speaker_name):
        with h5py.File(self.hdf5_file, "r") as hf:
            if speaker_name in hf:
                embeddings = hf[speaker_name]["embeddings"][:]
                return embeddings
            else:
                print(f"No embeddings found for speaker: {speaker_name}")
                return None

if __name__ == "__main__":
    # Example usage
    hdf5_file_path = "embeddings.hdf5"

    # Writing embeddings to HDF5
    embeddings_handler = EmbeddingsHDF5Handler(hdf5_file_path)
    embeddings_handler.write_embeddings(embeddings_list, speaker_names)

    # Reading embeddings from HDF5
    loaded_embeddings, loaded_speaker_names = embeddings_handler.read_embeddings()

    # Lookup embeddings for a specific speaker
    embeddings_handler = EmbeddingsHDF5Handler(hdf5_file_path)
    speaker_name_to_lookup = "John Doe"
    embeddings_for_speaker = embeddings_handler.get_embeddings_for_speaker(speaker_name_to_lookup)

    if embeddings_for_speaker is not None:
        print(f"Embeddings for {speaker_name_to_lookup}: {embeddings_for_speaker}")

