import os
import sys

# Thêm đường dẫn để test
sys.path.append(os.path.abspath("d:/Job-Market-Analytics-Platform/backend/chatbot"))
sys.path.append(os.path.abspath("d:/Job-Market-Analytics-Platform/chatbot/phase 3-semantic chunking"))
sys.path.append(os.path.abspath("d:/Job-Market-Analytics-Platform/chatbot/phase 4-validation and storage"))

from ner_extractor import PhoBERTNERExtractor
from embedder import ResumeEmbedder

def test_ner():
    print("Testing NER...")
    try:
        extractor = PhoBERTNERExtractor()
        res = extractor.extract_from_text("Nguyễn Văn A làm việc tại FPT")
        print("NER OK", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

def test_embedder():
    print("Testing Embedder (PyTorch)...")
    try:
        emb = ResumeEmbedder(backend="pytorch")
        res = emb.embed_query("test")
        print("PyTorch Embedder OK")
    except Exception as e:
        import traceback
        traceback.print_exc()

    print("Testing Embedder (ONNX)...")
    try:
        emb2 = ResumeEmbedder(backend="onnx")
        res2 = emb2.embed_query("test")
        print("ONNX Embedder OK")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ner()
    test_embedder()
