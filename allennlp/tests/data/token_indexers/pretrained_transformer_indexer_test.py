from transformers.tokenization_auto import AutoTokenizer

from allennlp.common.testing import AllenNlpTestCase
from allennlp.data import Token, Vocabulary
from allennlp.data.token_indexers import PretrainedTransformerIndexer
from allennlp.data.tokenizers import PretrainedTransformerTokenizer


class TestPretrainedTransformerIndexer(AllenNlpTestCase):
    def test_as_array_produces_token_sequence_bert_uncased(self):
        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        allennlp_tokenizer = PretrainedTransformerTokenizer("bert-base-uncased")
        indexer = PretrainedTransformerIndexer(model_name="bert-base-uncased")
        string_specials = "[CLS] AllenNLP is great [SEP]"
        string_no_specials = "AllenNLP is great"
        tokens = tokenizer.tokenize(string_specials)
        expected_ids = tokenizer.convert_tokens_to_ids(tokens)
        # tokens tokenized with our pretrained tokenizer have indices in them
        allennlp_tokens = allennlp_tokenizer.tokenize(string_no_specials)
        vocab = Vocabulary()
        indexed = indexer.tokens_to_indices(allennlp_tokens, vocab)
        assert indexed["token_ids"] == expected_ids

    def test_as_array_produces_token_sequence_bert_cased(self):
        tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
        allennlp_tokenizer = PretrainedTransformerTokenizer("bert-base-cased")
        indexer = PretrainedTransformerIndexer(model_name="bert-base-cased")
        string_specials = "[CLS] AllenNLP is great [SEP]"
        string_no_specials = "AllenNLP is great"
        tokens = tokenizer.tokenize(string_specials)
        expected_ids = tokenizer.convert_tokens_to_ids(tokens)
        # tokens tokenized with our pretrained tokenizer have indices in them
        allennlp_tokens = allennlp_tokenizer.tokenize(string_no_specials)
        vocab = Vocabulary()
        indexed = indexer.tokens_to_indices(allennlp_tokens, vocab)
        assert indexed["token_ids"] == expected_ids

    def test_as_array_produces_token_sequence_bert_cased_sentence_pair(self):
        tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
        allennlp_tokenizer = PretrainedTransformerTokenizer("bert-base-cased")
        indexer = PretrainedTransformerIndexer(model_name="bert-base-cased")
        default_format = "[CLS] AllenNLP is great! [SEP] Really it is! [SEP]"
        tokens = tokenizer.tokenize(default_format)
        expected_ids = tokenizer.convert_tokens_to_ids(tokens)
        allennlp_tokens = allennlp_tokenizer.tokenize_sentence_pair(
            "AllenNLP is great!", "Really it is!"
        )
        vocab = Vocabulary()
        indexed = indexer.tokens_to_indices(allennlp_tokens, vocab)
        assert indexed["token_ids"] == expected_ids

    def test_as_array_produces_token_sequence_roberta(self):
        tokenizer = AutoTokenizer.from_pretrained("roberta-base")
        allennlp_tokenizer = PretrainedTransformerTokenizer("roberta-base")
        indexer = PretrainedTransformerIndexer(model_name="roberta-base")
        string_specials = "<s> AllenNLP is great </s>"
        string_no_specials = "AllenNLP is great"
        tokens = tokenizer.tokenize(string_specials)
        expected_ids = tokenizer.convert_tokens_to_ids(tokens)
        # tokens tokenized with our pretrained tokenizer have indices in them
        allennlp_tokens = allennlp_tokenizer.tokenize(string_no_specials)
        vocab = Vocabulary()
        indexed = indexer.tokens_to_indices(allennlp_tokens, vocab)
        assert indexed["token_ids"] == expected_ids

    def test_as_array_produces_token_sequence_roberta_sentence_pair(self):
        tokenizer = AutoTokenizer.from_pretrained("roberta-base")
        allennlp_tokenizer = PretrainedTransformerTokenizer("roberta-base")
        indexer = PretrainedTransformerIndexer(model_name="roberta-base")
        default_format = "<s> AllenNLP is great! </s> </s> Really it is! </s>"
        tokens = tokenizer.tokenize(default_format)
        expected_ids = tokenizer.convert_tokens_to_ids(tokens)
        allennlp_tokens = allennlp_tokenizer.tokenize_sentence_pair(
            "AllenNLP is great!", "Really it is!"
        )
        vocab = Vocabulary()
        indexed = indexer.tokens_to_indices(allennlp_tokens, vocab)
        assert indexed["token_ids"] == expected_ids

    def test_transformers_vocab_sizes(self):
        def check_vocab_size(model_name: str):
            namespace = "tags"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            allennlp_tokenizer = PretrainedTransformerTokenizer(model_name)
            indexer = PretrainedTransformerIndexer(model_name=model_name, namespace=namespace)
            allennlp_tokens = allennlp_tokenizer.tokenize("AllenNLP is great!")
            vocab = Vocabulary()
            # here we copy entire transformers vocab
            indexed = indexer.tokens_to_indices(allennlp_tokens, vocab)
            del indexed
            assert vocab.get_vocab_size(namespace=namespace) == tokenizer.vocab_size

        check_vocab_size("roberta-base")
        check_vocab_size("bert-base-cased")
        check_vocab_size("xlm-mlm-ende-1024")

    def test_transformers_vocabs_added_correctly(self):
        namespace, model_name = "tags", "roberta-base"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        allennlp_tokenizer = PretrainedTransformerTokenizer(model_name)
        indexer = PretrainedTransformerIndexer(model_name=model_name, namespace=namespace)
        allennlp_tokens = allennlp_tokenizer.tokenize("AllenNLP is great!")
        vocab = Vocabulary()
        # here we copy entire transformers vocab
        indexed = indexer.tokens_to_indices(allennlp_tokens, vocab)
        del indexed
        assert vocab.get_token_to_index_vocabulary(namespace=namespace) == tokenizer.encoder

    def test_mask(self):
        allennlp_tokenizer = PretrainedTransformerTokenizer("bert-base-uncased")
        indexer = PretrainedTransformerIndexer(model_name="bert-base-uncased")
        string_no_specials = "AllenNLP is great"
        allennlp_tokens = allennlp_tokenizer.tokenize(string_no_specials)
        vocab = Vocabulary()
        indexed = indexer.tokens_to_indices(allennlp_tokens, vocab)
        expected_masks = [1] * len(indexed["token_ids"])
        assert indexed["mask"] == expected_masks
        max_length = 10
        padding_lengths = {"token_ids": max_length, "mask": max_length}
        padded_tokens = indexer.as_padded_tensor_dict(indexed, padding_lengths)
        padding_length = max_length - len(indexed["mask"])
        expected_masks = expected_masks + ([0] * padding_length)
        assert len(padded_tokens["mask"]) == max_length
        assert padded_tokens["mask"].tolist() == expected_masks
