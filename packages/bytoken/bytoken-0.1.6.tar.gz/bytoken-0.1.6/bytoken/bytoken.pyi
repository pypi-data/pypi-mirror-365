class ByToken:
    """
    A high-performance Byte-Pair Encoding (BPE) tokenizer implemented in C++
    with a Python interface.
    """

    def __init__(self) -> None:
        """Initializes a new, empty tokenizer instance."""
        ...

    def train(self, text_corpus: str, vocab_size: int, verbose: bool = False) -> None:
        """
        Trains the tokenizer on a given text corpus to build a vocabulary of a specified size.

        Args:
            text_corpus: The raw string data to train on.
            vocab_size: The target size of the final vocabulary.
            verbose: If True, prints training progress.
        """
        ...

    def encode(self, text: str) -> list[int]:
        """
        Encodes a string into a list of token IDs.

        Args:
            text: The input string to encode.

        Returns:
            A list of integers representing the token IDs.
        """
        ...

    def decode(self, idx: list[int]) -> str:
        """
        Decodes a list of token IDs back into a string.

        Args:
            idx: A list of token IDs.

        Returns:
            The reconstructed string.
        """
        ...

    def save(self, path: str) -> None:
        """
        Saves the tokenizer's state (vocabulary and merges) to a JSON file.

        This method is implemented in Python and handles the serialization.

        Args:
            path: The file path to save the tokenizer to.
        """
        ...

    def from_file(self, path: str) -> None:
        """
        Loads a tokenizer's state from a JSON file into the current instance.

        This method is implemented in Python and handles deserialization.

        Args:
            path: The file path of the tokenizer model to load.
        """
        ...