"""Data loading utilities for the Transformer Algebra project.

This module defines helper functions that build the training and evaluation
`Dataset`, `Tokenizer`, and `DataCollator` objects used throughout the
library.  In particular, the `load_data` factory translates symbolic
polynomial expressions into the internal token representation expected by the
Transformer models.
"""

import yaml
import logging
from .utils.data_collator import (
    StandardDataset,
    StandardDataCollator,
    _read_data_from_file,
)
from .utils.preprocessor import (
    IntegerToInternalProcessor,
    PolynomialToInternalProcessor,
)
from .utils.tokenizer import VocabConfig, set_tokenizer
from transformers import PreTrainedTokenizerFast as StandardTokenizer


logger = logging.getLogger(__name__)


def load_data(
    train_dataset_path: str,
    test_dataset_path: str,
    field: str,
    num_variables: int,
    max_degree: int,
    max_coeff: int,
    max_length: int = 512,
    processor_name: str = "polynomial",
    vocab_path: str | None = None,
    num_train_samples: int | None = None,
    num_test_samples: int | None = None,
) -> tuple[dict[str, StandardDataset], StandardTokenizer, StandardDataCollator]:
    """Create dataset, tokenizer and data-collator objects.

    Parameters
    ----------
    train_dataset_path : str
        Path to the file that stores the *training* samples.
    test_dataset_path : str
        Path to the file that stores the *evaluation* samples.
    field : str
        Finite-field identifier (e.g. ``"Q"`` for the rationals or ``"Zp"``
        for a prime field) used to generate the vocabulary.
    num_variables : int
        Maximum number of symbolic variables (\\(x_1, \\dots, x_n\\)) that can
        appear in a polynomial.
    max_degree : int
        Maximum total degree allowed for any monomial term.
    max_coeff : int
        Maximum absolute value of the coefficients appearing in the data.
    max_length : int, default ``512``
        Hard upper bound on the token sequence length.  Longer sequences will
        be *right-truncated*.
    processor_name : str, default ``"polynomial"``
        Name of the processor to use for converting symbolic expressions into
        internal token IDs.  The default processor is ``"polynomial"``, which
        handles polynomial expressions.  The alternative processor is
        ``"integer"``, which handles integer expressions.
    vocab_path : str | None, default ``None``
        Path to the vocabulary configuration file. If None, a default vocabulary
        will be generated based on the field, max_degree, and max_coeff parameters.
    num_train_samples : int | None, default ``None``
        Maximum number of training samples to load. If None or -1, all available
        training samples will be loaded.
    num_test_samples : int | None, default ``None``
        Maximum number of test samples to load. If None or -1, all available
        test samples will be loaded.

    Returns
    -------
    tuple[dict[str, StandardDataset], StandardTokenizer, StandardDataCollator]
        1. ``dataset``  - a ``dict`` with ``"train"`` and ``"test"`` splits
           containing :class:`StandardDataset` instances.
        2. ``tokenizer`` - a :class:`PreTrainedTokenizerFast` capable of
           encoding symbolic expressions into token IDs and vice versa.
        3. ``data_collator`` - a callable that assembles batches and applies
           dynamic padding so they can be fed to a HuggingFace ``Trainer``.
    """
    if processor_name == "polynomial":
        preprocessor = PolynomialToInternalProcessor(
            num_variables=num_variables,
            max_degree=max_degree,
            max_coeff=max_coeff,
        )
    elif processor_name == "integer":
        preprocessor = IntegerToInternalProcessor(max_coeff=max_coeff)
    else:
        raise ValueError(f"Unknown processor: {processor_name}")

    train_input_texts, train_target_texts = _read_data_from_file(
        train_dataset_path, max_samples=num_train_samples
    )
    train_dataset = StandardDataset(
        input_texts=train_input_texts,
        target_texts=train_target_texts,
        preprocessor=preprocessor,
    )

    test_input_texts, test_target_texts = _read_data_from_file(
        test_dataset_path, max_samples=num_test_samples
    )
    test_dataset = StandardDataset(
        input_texts=test_input_texts,
        target_texts=test_target_texts,
        preprocessor=preprocessor,
    )

    vocab_config: VocabConfig | None = None
    if vocab_path:
        with open(vocab_path, "r") as f:
            vocab_config = yaml.safe_load(f)

    tokenizer = set_tokenizer(
        field=field,
        max_degree=max_degree,
        max_coeff=max_coeff,
        max_length=max_length,
        vocab_config=vocab_config,
    )
    data_collator = StandardDataCollator(tokenizer)
    dataset = {"train": train_dataset, "test": test_dataset}
    return dataset, tokenizer, data_collator
