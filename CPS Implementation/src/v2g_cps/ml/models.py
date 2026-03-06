from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


class LSTMClassifier(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 32, num_layers: int = 2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2,
        )
        self.head = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        outputs, _ = self.lstm(inputs)
        return self.head(outputs[:, -1, :]).squeeze(-1)


class MLPBaseline(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        flattened = inputs.reshape(inputs.size(0), -1)
        return self.layers(flattened).squeeze(-1)


@dataclass(slots=True)
class TrainingBundle:
    train_loader: DataLoader
    val_loader: DataLoader
    test_loader: DataLoader


def build_loader(features: np.ndarray, labels: np.ndarray, batch_size: int, shuffle: bool) -> DataLoader:
    dataset = TensorDataset(
        torch.tensor(features, dtype=torch.float32),
        torch.tensor(labels, dtype=torch.float32),
    )
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def train_binary_model(
    model: nn.Module,
    *,
    bundle: TrainingBundle,
    epochs: int,
    learning_rate: float,
    device: torch.device,
) -> nn.Module:
    model.to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    best_state = None
    best_val_loss = float("inf")

    for _ in range(epochs):
        model.train()
        for features, labels in bundle.train_loader:
            features = features.to(device)
            labels = labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(features)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

        model.eval()
        losses = []
        with torch.no_grad():
            for features, labels in bundle.val_loader:
                features = features.to(device)
                labels = labels.to(device)
                logits = model(features)
                losses.append(float(criterion(logits, labels).cpu()))
        mean_loss = float(np.mean(losses))
        if mean_loss < best_val_loss:
            best_val_loss = mean_loss
            best_state = {name: tensor.detach().cpu().clone() for name, tensor in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)
    return model.cpu()


def evaluate_binary_model(model: nn.Module, loader: DataLoader) -> dict[str, object]:
    model.eval()
    probabilities: list[float] = []
    labels: list[int] = []
    with torch.no_grad():
        for features, batch_labels in loader:
            logits = model(features)
            probs = torch.sigmoid(logits).cpu().numpy()
            probabilities.extend(float(item) for item in probs)
            labels.extend(int(item) for item in batch_labels.cpu().numpy())

    predicted = [1 if item >= 0.5 else 0 for item in probabilities]
    metrics = {
        "accuracy": round(float(accuracy_score(labels, predicted)), 4),
        "precision": round(float(precision_score(labels, predicted, zero_division=0)), 4),
        "recall": round(float(recall_score(labels, predicted, zero_division=0)), 4),
        "f1": round(float(f1_score(labels, predicted, zero_division=0)), 4),
        "false_positive_rate": round(
            float(confusion_matrix(labels, predicted, labels=[0, 1])[0, 1] / max(sum(label == 0 for label in labels), 1)),
            4,
        ),
        "confusion_matrix": confusion_matrix(labels, predicted, labels=[0, 1]).tolist(),
    }
    try:
        metrics["roc_auc"] = round(float(roc_auc_score(labels, probabilities)), 4)
    except ValueError:
        metrics["roc_auc"] = None
    return metrics

