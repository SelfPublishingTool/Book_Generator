import torch
import time

print(f"Torch version: {torch.__version__}")
print(f"MPS available: {torch.backends.mps.is_available()}")
print(f"MPS built: {torch.backends.mps.is_built()}")

if torch.backends.mps.is_available():
    device = torch.device("mps")
    # Test velocità semplice
    x = torch.randn(2000, 2000).to(device)
    start = time.time()
    for _ in range(100):
        y = torch.matmul(x, x)
    torch.mps.synchronize()
    end = time.time()
    print(f"Tempo per 100 moltiplicazioni matriciali su MPS: {end - start:.4f}s")
else:
    print("MPS NON DISPONIBILE! Ecco perché era lento.")
