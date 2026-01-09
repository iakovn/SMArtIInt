# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     name: dev
#     display_name: Python (dev)
#     language: python
# ---
#
# %%
import os

import numpy as np
import torch
import torch.nn as nn


class PyTorchPIController(nn.Module):
    """
    A PyTorch implementation of the PI controller RNN.
    This model mimics the structure of the TensorFlow version.
    """

    def __init__(self):
        super(PyTorchPIController, self).__init__()
        # A simple RNN with 1 input feature, 2 hidden units
        self.rnn = nn.RNN(input_size=1, hidden_size=2, batch_first=True, bias=False)
        # A dense layer to produce the single output value
        self.dense = nn.Linear(in_features=2, out_features=1, bias=False)

    def forward(self, x, hidden_state):
        """
        Forward pass for the model.
        Args:
            x: The input tensor (batch, sequence, features).
            hidden_state: The initial hidden state for the RNN.
        Returns:
            A tuple containing the output and the new hidden state.
        """
        rnn_out, new_hidden_state = self.rnn(x, hidden_state)
        output = self.dense(rnn_out)
        return output, new_hidden_state


def generate_and_export_pytorch_pi(k=30, T=1600, tau=10):
    """
    Generates the PyTorch PI controller model, sets its weights,
    and exports it.
    """
    print("Creating PyTorch PI controller model...")
    model = PyTorchPIController()

    # --- Manually set weights to mimic PI controller ---
    # This is equivalent to the set_weights calls in the TensorFlow script.
    # Note: PyTorch weight dimensions are often transposed compared to TensorFlow.

    # Set weights for the dense layer
    # TF shape: (2, 1), PyTorch shape: (1, 2)
    dense_weights = torch.tensor([[k / T * tau, k]], dtype=torch.float32)
    model.dense.weight = nn.Parameter(dense_weights)

    # Set weights for the RNN layer
    # input-to-hidden weights (TF shape: (1, 2), PyTorch shape: (2, 1))
    w_ih = torch.tensor([[0.0], [1.0]], dtype=torch.float32)
    # hidden-to-hidden weights (TF shape: (2, 2), PyTorch shape: (2, 2))
    w_hh = torch.tensor([[1.0, 0.0], [1.0, 0.0]], dtype=torch.float32)
    model.rnn.weight_ih_l0 = nn.Parameter(w_ih)
    model.rnn.weight_hh_l0 = nn.Parameter(w_hh)

    print("Model weights set to mimic PI controller.")

    # --- Export the model to ONNX ---
    # The ONNX exporter needs dummy inputs to trace the model's execution.
    # The shape and type of these inputs must match what the model expects.
    output_path = os.path.join('.', "PI_stateful_torch.onnx")
    
    # Dummy inputs for tracing:
    # x: (batch_size, sequence_length, input_features)
    dummy_input_x = torch.randn(1, 1, 1) 
    # hidden_state: (num_layers, batch_size, hidden_size)
    dummy_hidden_state = torch.randn(1, 1, 2)

    # The names for inputs and outputs are important for the C++ interface.
    input_names = ["FeatureInput", "HiddenStateInput"]
    output_names = ["ModelOutput", "HiddenStateOutput"]

    torch.onnx.export(
        model,
        (dummy_input_x, dummy_hidden_state),
        output_path,
        input_names=input_names,
        output_names=output_names,
        opset_version=13, # Use a reasonably modern opset
        dynamic_axes={
            'FeatureInput': {0: 'batch_size', 1: 'sequence_length'},
            'HiddenStateInput': {1: 'batch_size'},
            'ModelOutput': {0: 'batch_size', 1: 'sequence_length'},
            'HiddenStateOutput': {1: 'batch_size'}
        }
    )
    
    print(f"PyTorch model exported to ONNX format at: {output_path}")

    return model


def test_pytorch_model(model, height=1.0, duration=3600, start=500, tau=10):
    """
    Performs a simple step test to verify the PyTorch model's behavior.
    """
    print("\nTesting PyTorch model...")
    times = np.arange(0, duration, tau)
    step_data = np.zeros_like(times, dtype=np.float32)
    step_data[times >= start] = height

    results = []
    # Initial hidden state (batch_size=1, num_layers=1, hidden_size=2)
    hidden = torch.zeros((1, 1, 2), dtype=torch.float32)

    model.eval()  # Set the model to evaluation mode
    with torch.no_grad():  # Disable gradient calculation for inference
        for val in step_data:
            # Input needs to be shaped as (batch, seq_len, features)
            input_tensor = torch.tensor([[[val]]], dtype=torch.float32)
            output, hidden = model(input_tensor, hidden)
            results.append(output.item())

    # A simple check to see if the output looks reasonable
    print(f"Test simulation finished. Number of results: {len(results)}")
    print(f"Final output value: {results[-1]:.2f}")
    # A proper plot would require matplotlib, which is not imported here
    # to keep the script focused on the model itself.


# %%
if __name__ == "__main__":
    # Use the same parameters as the original script for consistency
    k_gain = 30
    T_time_constant = 1600
    tau_sample_time = 10

    pytorch_model = generate_and_export_pytorch_pi(
        k=k_gain, T=T_time_constant, tau=tau_sample_time
    )
    test_pytorch_model(pytorch_model, tau=tau_sample_time)
