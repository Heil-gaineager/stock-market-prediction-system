import torch
import torch.nn as nn

class TransformerBlock(nn.Module):
    def __init__(self, embed_size, heads, dropout, forward_expansion):
        super(TransformerBlock, self).__init__()
        self.attention = nn.MultiheadAttention(embed_dim=embed_size, num_heads=heads)
        self.norm1 = nn.LayerNorm(embed_size)
        self.norm2 = nn.LayerNorm(embed_size)
        self.feed_forward = nn.Sequential(
            nn.Linear(embed_size, forward_expansion * embed_size),
            nn.ReLU(),
            nn.Linear(forward_expansion * embed_size, embed_size)
        )
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, value, key, query, mask):
        attention = self.attention(query, key, value, attn_mask=mask)[0]
        x = self.dropout1(attention) + query
        x = self.norm1(x)
        forward = self.feed_forward(x)
        out = self.dropout2(forward) + x
        return self.norm2(out)

class TransformerModel(nn.Module):
    def __init__(self, embed_size, heads, num_layers, dropout, forward_expansion, input_length, output_length):
        super(TransformerModel, self).__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.num_layers = num_layers
        self.dropout = dropout
        self.forward_expansion = forward_expansion
        self.input_length = input_length
        self.output_length = output_length
        self.transformer_blocks = nn.ModuleList(
            [TransformerBlock(embed_size, heads, dropout, forward_expansion) for _ in range(num_layers)]
        )
        self.fc_out = nn.Linear(embed_size * input_length, output_length)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        for layer in self.transformer_blocks:
            x = layer(x, x, x, None)
        x = x.view(x.shape[0], -1)
        out = self.fc_out(x)
        return out  
