"""
Attention Bi-LSTM architecture for Bio-Sniff Crop Disease Classifier.
Matches the trained Bio-Sniff ML model specifications:
- input_dim = 6: [Temperature, Humidity, Pressure, Gas Resistance, Gas Difference, Gas Ratio]
- hidden_dim = 128 (bidirectional -> 256 per step)
- num_layers = 2
- num_classes = 5
- dropout = 0.3
- sequence shape: (batch_size, 50, 6)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class Attention(nn.Module):
    """
    Time-step attention mechanism for sequence classification.
    Calculates attention weights across 50 time steps and pools the Bi-LSTM
    hidden states into a 256-dimensional context vector.
    """
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.attn = nn.Linear(hidden_dim, 1)

    def forward(self, x: torch.Tensor):
        # x shape: (batch, seq_len, hidden_dim) where hidden_dim is bidirectional (256)
        scores = self.attn(x)  # (batch, seq_len, 1)
        weights = F.softmax(scores, dim=1)  # Softmax over seq_len (50)
        context = torch.sum(weights * x, dim=1)  # (batch, hidden_dim)
        return context, weights


class AttentionBiLSTM(nn.Module):
    """
    Trained Attention Bi-LSTM model architecture for Bio-Sniff.
    """
    def __init__(
        self,
        input_dim: int = 6,
        hidden_dim: int = 128,
        num_layers: int = 2,
        num_classes: int = 5,
        dropout: float = 0.3
    ):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_classes = num_classes
        self.dropout_rate = dropout

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        # Bidirectional LSTM has hidden_dim * 2 features
        self.attention = Attention(hidden_dim * 2)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        :param x: Tensor of shape (batch, 50, 6)
        :return: Logits of shape (batch, 5)
        """
        lstm_out, _ = self.lstm(x)  # (batch, 50, 256)
        context, _ = self.attention(lstm_out)  # (batch, 256)
        out = self.dropout(context)
        logits = self.fc(out)  # (batch, 5)
        return logits
