#!/usr/bin/env python3
"""passgpt_gen.py — Genera contrasenas del GPT entrenado a un fichero (--out)."""
import argparse, sys, torch, torch.nn as nn
from torch.nn import functional as F

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="passgpt_model.pt")
ap.add_argument("--out", default="passgpt_candidates.txt")
ap.add_argument("--num", type=int, default=10_000_000)
ap.add_argument("--batch", type=int, default=4096)
ap.add_argument("--temperature", type=float, default=1.0)
ap.add_argument("--device", default="cuda")
args = ap.parse_args()

device = args.device if (args.device == "cpu" or torch.cuda.is_available()) else "cpu"
ckpt = torch.load(args.model, map_location=device)
vocab, stoi, cfg = ckpt["vocab"], ckpt["stoi"], ckpt["config"]
V, block = cfg["V"], cfg["block"]
pad_id, bos_id, eos_id = stoi["\x00"], stoi["\x02"], stoi["\x03"]

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
        return self.head(self.lnf(x)), None

model = GPT(V, block, cfg["layers"], cfg["heads"], cfg["embd"]).to(device)
model.load_state_dict(ckpt["model"]); model.eval()

@torch.no_grad()
def generate_batch(B):
    seqs = torch.full((B, 1), bos_id, dtype=torch.long, device=device)
    done = torch.zeros(B, dtype=torch.bool, device=device)
    for _ in range(block - 1):
        logits, _ = model(seqs)
        p = F.softmax(logits[:, -1] / args.temperature, dim=-1)
        nxt = torch.multinomial(p, 1)
        seqs = torch.cat([seqs, nxt], dim=1)
        done = done | (nxt.squeeze(1) == eos_id)
        if bool(done.all()): break
    return seqs.tolist()

written = 0
with open(args.out, "w", encoding="utf-8") as f:
    while written < args.num:
        B = min(args.batch, args.num - written)
        for s in generate_batch(B):
            chars = []
            for i in s[1:]:
                if i == eos_id or i == pad_id: break
                chars.append(vocab[i])
            pw = "".join(chars)
            if pw:
                f.write(pw + "\n"); written += 1
print(f"Generadas {written:,} contrasenas -> {args.out}", file=sys.stderr)
