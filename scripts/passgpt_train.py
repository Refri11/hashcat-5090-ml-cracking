#!/usr/bin/env python3
"""passgpt_train.py — GPT char-level sobre un corpus de contrasenas."""
import argparse, time
import torch, torch.nn as nn
from torch.nn import functional as F

ap = argparse.ArgumentParser()
ap.add_argument("--data", default="train.txt")
ap.add_argument("--out", default="passgpt_model.pt")
ap.add_argument("--block", type=int, default=32)
ap.add_argument("--layers", type=int, default=4)
ap.add_argument("--heads", type=int, default=4)
ap.add_argument("--embd", type=int, default=256)
ap.add_argument("--batch", type=int, default=256)
ap.add_argument("--iters", type=int, default=5000)
ap.add_argument("--lr", type=float, default=3e-4)
ap.add_argument("--device", default="cuda")
ap.add_argument("--max_rows", type=int, default=0)
args = ap.parse_args()

device = args.device if (args.device == "cpu" or torch.cuda.is_available()) else "cpu"
BOS, EOS, PAD = "\x02", "\x03", "\x00"

print(f"Cargando {args.data} ...")
pws = []
with open(args.data, encoding="utf-8") as f:
    for line in f:
        pw = line.rstrip("\r\n")
        if not pw or len(pw) > args.block - 2: continue
        pws.append(pw)
        if args.max_rows and len(pws) >= args.max_rows: break
print(f"  {len(pws):,} contrasenas")

chars = sorted(set("".join(pws)))
vocab = [PAD, BOS, EOS] + chars
stoi = {c: i for i, c in enumerate(vocab)}
V = len(vocab); pad_id = stoi[PAD]
assert V < 256
print(f"  vocabulario: {V}")

data = torch.zeros(len(pws), args.block, dtype=torch.uint8)
for i, pw in enumerate(pws):
    ids = [stoi[BOS]] + [stoi[c] for c in pw] + [stoi[EOS]]
    data[i, :len(ids)] = torch.tensor(ids, dtype=torch.uint8)
print(f"  tensor: {tuple(data.shape)}")

def get_batch():
    idx = torch.randint(0, data.size(0), (args.batch,))
    b = data[idx].to(device).long()
    return b[:, :-1], b[:, 1:]

class Block(nn.Module):
    def __init__(self, n_embd, n_head, block):
        super().__init__()
        self.ln1 = nn.LayerNorm(n_embd)
        self.attn = nn.MultiheadAttention(n_embd, n_head, batch_first=True)
        self.ln2 = nn.LayerNorm(n_embd)
        self.mlp = nn.Sequential(nn.Linear(n_embd, 4*n_embd), nn.GELU(), nn.Linear(4*n_embd, n_embd))
        self.register_buffer("mask", torch.triu(torch.full((block, block), float("-inf")), diagonal=1))
    def forward(self, x):
        T = x.size(1)
        h = self.ln1(x)
        a, _ = self.attn(h, h, h, attn_mask=self.mask[:T, :T], need_weights=False)
        x = x + a
        return x + self.mlp(self.ln2(x))

class GPT(nn.Module):
    def __init__(self, V, block, n_layer, n_head, n_embd):
        super().__init__()
        self.tok = nn.Embedding(V, n_embd)
        self.pos = nn.Embedding(block, n_embd)
        self.blocks = nn.ModuleList([Block(n_embd, n_head, block) for _ in range(n_layer)])
        self.lnf = nn.LayerNorm(n_embd)
        self.head = nn.Linear(n_embd, V)
    def forward(self, idx, targets=None):
        T = idx.size(1)
        pos = torch.arange(T, device=idx.device)
        x = self.tok(idx) + self.pos(pos)[None, :, :]
        for blk in self.blocks: x = blk(x)
        logits = self.head(self.lnf(x))
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1), ignore_index=pad_id)
        return logits, loss

model = GPT(V, args.block, args.layers, args.heads, args.embd).to(device)
print(f"Modelo: {sum(p.numel() for p in model.parameters())/1e6:.2f}M parametros en {device}")

@torch.no_grad()
def sample(n=8, temperature=1.0):
    model.eval(); out = []
    for _ in range(n):
        ids = [stoi[BOS]]
        for _ in range(args.block - 1):
            x = torch.tensor([ids], dtype=torch.long, device=device)
            logits, _ = model(x)
            p = F.softmax(logits[0, -1] / temperature, dim=-1)
            nxt = torch.multinomial(p, 1).item()
            if nxt in (stoi[EOS], pad_id): break
            ids.append(nxt)
        out.append("".join(vocab[i] for i in ids[1:]))
    model.train(); return out

opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
t0 = time.time()
for it in range(1, args.iters + 1):
    x, y = get_batch()
    _, loss = model(x, y)
    opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
    if it == 1 or it % 100 == 0:
        print(f"  iter {it:5d}/{args.iters}  loss {loss.item():.4f}  ({time.time()-t0:.0f}s)")
    if it % 1000 == 0:
        print("   muestras:", ", ".join(sample(6)))

torch.save({"model": model.state_dict(), "vocab": vocab, "stoi": stoi,
            "config": {"V": V, "block": args.block, "layers": args.layers, "heads": args.heads, "embd": args.embd}}, args.out)
print(f"Guardado -> {args.out}")
print("Muestras finales:", ", ".join(sample(12)))
