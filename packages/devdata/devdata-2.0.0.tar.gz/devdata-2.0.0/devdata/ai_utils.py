"""
ai_utils.py

Powerful, easy-to-use AI utilities with unified PyTorch and TensorFlow/Keras support,
covering CNNs, RNNs, Transformers, and large language models (LLMs), including chatbot training.

Dependencies:
- torch
- torchvision
- tensorflow
- transformers
- datasets

Install with:
pip install torch torchvision tensorflow transformers datasets
"""

import os
import numpy as np
from typing import Optional, List, Callable, Dict, Any, Union

# Detect backends
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow.keras import layers, models, optimizers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

from transformers import (
    AutoModelForCausalLM, AutoTokenizer,
    TFAutoModelForCausalLM, 
    pipeline
)

# ---------------------------
# Backend Selector
# ---------------------------

class AIBackend:
    PYTORCH = 'pytorch'
    TENSORFLOW = 'tensorflow'

# ---------------------------
# Dataset Wrappers (PyTorch & TF)
# ---------------------------

if TORCH_AVAILABLE:
    class TorchDataset(Dataset):
        def __init__(self, data, labels, transform=None):
            self.data = data
            self.labels = labels
            self.transform = transform

        def __len__(self):
            return len(self.data)

        def __getitem__(self, idx):
            x = self.data[idx]
            if self.transform:
                x = self.transform(x)
            y = self.labels[idx]
            return x, y

    def create_torch_dataloader(data, labels, batch_size=32, shuffle=True, transform=None):
        dataset = TorchDataset(data, labels, transform)
        return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

if TF_AVAILABLE:
    def create_tf_dataset(data, labels, batch_size=32, shuffle=True, transform: Optional[Callable] = None):
        dataset = tf.data.Dataset.from_tensor_slices((data, labels))
        if shuffle:
            dataset = dataset.shuffle(buffer_size=len(data))
        if transform:
            dataset = dataset.map(transform)
        dataset = dataset.batch(batch_size)
        return dataset

# ---------------------------
# CNN Model Builders
# ---------------------------

def build_cnn_pytorch(input_channels=3, num_classes=10):
    assert TORCH_AVAILABLE, "PyTorch is not installed."

    class SimpleCNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(input_channels, 32, 3, padding=1),
                nn.ReLU(inplace=True),
                nn.BatchNorm2d(32),
                nn.MaxPool2d(2),

                nn.Conv2d(32, 64, 3, padding=1),
                nn.ReLU(inplace=True),
                nn.BatchNorm2d(64),
                nn.MaxPool2d(2),

                nn.Conv2d(64, 128, 3, padding=1),
                nn.ReLU(inplace=True),
                nn.BatchNorm2d(128),
                nn.MaxPool2d(2),
            )
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(128 * 4 * 4, 256),
                nn.ReLU(inplace=True),
                nn.Dropout(0.5),
                nn.Linear(256, num_classes)
            )
        def forward(self, x):
            x = self.features(x)
            x = self.classifier(x)
            return x

    return SimpleCNN()

def build_cnn_tf(input_shape=(32,32,3), num_classes=10):
    assert TF_AVAILABLE, "TensorFlow is not installed."
    model = models.Sequential([
        layers.Conv2D(32, 3, padding='same', activation='relu', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.MaxPooling2D(),

        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(),

        layers.Conv2D(128, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(),

        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(num_classes)
    ])
    return model

# ---------------------------
# Training Utilities
# ---------------------------

def train_pytorch(model, dataloader, criterion, optimizer,
                  epochs=10, device=None, verbose=True):
    assert TORCH_AVAILABLE, "PyTorch is not installed."
    device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.train()

    for epoch in range(epochs):
        running_loss = 0.0
        correct = 0
        total = 0
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)

        epoch_loss = running_loss / total
        accuracy = correct / total
        if verbose:
            print(f"Epoch {epoch+1}/{epochs} - Loss: {epoch_loss:.4f} - Acc: {accuracy:.4f}")
    return model

def train_tf(model, train_dataset, val_dataset=None, epochs=10, verbose=True):
    assert TF_AVAILABLE, "TensorFlow is not installed."
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])
    history = model.fit(train_dataset, validation_data=val_dataset, epochs=epochs, verbose=verbose)
    return model, history

# ---------------------------
# Transformer & LLM Helpers (HuggingFace)
# ---------------------------

class LLMChatbot:
    def __init__(self, model_name: str = "gpt2", backend: str = AIBackend.PYTORCH, device: Optional[str] = None):
        self.backend = backend
        self.device = device
        if backend == AIBackend.PYTORCH:
            assert TORCH_AVAILABLE, "PyTorch not installed."
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(self.device)
        elif backend == AIBackend.TENSORFLOW:
            assert TF_AVAILABLE, "TensorFlow not installed."
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = TFAutoModelForCausalLM.from_pretrained(model_name)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def generate(self, prompt: str, max_length: int = 100, temperature: float = 0.7, top_k: int = 50):
        if self.backend == AIBackend.PYTORCH:
            inputs = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                temperature=temperature,
                top_k=top_k,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        elif self.backend == AIBackend.TENSORFLOW:
            inputs = self.tokenizer(prompt, return_tensors='tf')
            outputs = self.model.generate(
                inputs['input_ids'],
                max_length=max_length,
                temperature=temperature,
                top_k=top_k,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def chat(self, prompt: str, max_turns: int = 5):
        conversation = prompt
        for _ in range(max_turns):
            response = self.generate(conversation)
            conversation += "\n" + response
        return conversation

# ---------------------------
# Export / Save / Load Models
# ---------------------------

def save_pytorch_model(model: nn.Module, path: str):
    torch.save(model.state_dict(), path)

def load_pytorch_model(model_class: Callable, path: str, *args, **kwargs):
    model = model_class(*args, **kwargs)
    model.load_state_dict(torch.load(path))
    return model

def save_tf_model(model: tf.keras.Model, path: str):
    model.save(path)

def load_tf_model(path: str):
    return tf.keras.models.load_model(path)

# ---------------------------
# Example Usage / Demo
# ---------------------------

if __name__ == "__main__":
    print("AI Utils Demo Starting...")

    # Simple CNN training example (PyTorch)
    if TORCH_AVAILABLE:
        print("PyTorch CNN example:")
        import torchvision.transforms as transforms
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
        from torchvision.datasets import CIFAR10
        trainset = CIFAR10(root='./data', train=True, download=True, transform=transform)
        trainloader = DataLoader(trainset, batch_size=64, shuffle=True)
        cnn = build_cnn_pytorch(input_channels=3, num_classes=10)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(cnn.parameters(), lr=0.001)
        cnn = train_pytorch(cnn, trainloader, criterion, optimizer, epochs=1)

    # Simple CNN training example (TensorFlow)
    if TF_AVAILABLE:
        print("TensorFlow CNN example:")
        (x_train, y_train), _ = tf.keras.datasets.cifar10.load_data()
        x_train = x_train.astype('float32') / 255.0
        y_train = y_train.flatten()
        train_dataset = create_tf_dataset(x_train, y_train, batch_size=64)
        cnn_tf = build_cnn_tf(input_shape=(32,32,3), num_classes=10)
        cnn_tf, history = train_tf(cnn_tf, train_dataset, epochs=1)

    # LLM chatbot demo
    print("LLM chatbot example:")
    llm = LLMChatbot(model_name="gpt2", backend=AIBackend.PYTORCH if TORCH_AVAILABLE else AIBackend.TENSORFLOW)
    prompt = "Hello, how are you?"
    response = llm.generate(prompt, max_length=50)
    print(f"Prompt: {prompt}\nResponse: {response}")

    print("AI Utils Demo Complete.")
