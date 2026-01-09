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

# %% [markdown]
# # SMArtInt Simulation with OpenModelica and PyFMI
# This file is inteded to be run as a notebook (jupytext mode)
# It demonstrates how to run a simulation of the `TestPipe_tflite` example
#  from the SMArtInt library using OpenModelica via OMPython, and then uses
#  PyFMI to read and plot the results.

# %% [markdown]
# This notebook runs a simulation of the `TestPipe_tflite` example from the SMArtInt library using OpenModelica via OMPython, and then uses PyFMI to read and plot the results from a dedicated output directory.

# %%
import os
import matplotlib.pyplot as plt
from OMPython import OMCSessionZMQ
from pyfmi.common.io import ResultDymolaBinary, VariableNotFoundError

# %% [markdown]
# ## 1. Configure Environment and Load Libraries

# %%
omc = OMCSessionZMQ()

def send_omc_command(command):
    """A wrapper for omc.sendExpression that checks for errors."""
    result = omc.sendExpression(command)
    if result is None or (isinstance(result, dict) and 'messages' in result and 'Failed' in result['messages']):
        error_string = omc.sendExpression('getErrorString()')
        raise RuntimeError(f'OMC command failed: {command}\nError: {error_string}')
    return result

# Define project paths
project_root = os.path.abspath(os.path.join(os.getcwd(), '..', '..', '..'))
output_dir = os.path.join(project_root, 'generated')
os.makedirs(output_dir, exist_ok=True)
print(f'Project Root: {project_root}')
print(f'Simulation output will be stored in: {output_dir}')

# %%
# Set the working directory for the OMC session where files will be generated
send_omc_command(f'cd("{output_dir}")')

# %%
# Install and load the Modelica Standard Library if it is not already present
if not send_omc_command('loadModel(Modelica)'):
    print('Modelica Standard Library not found. Installing...')
    send_omc_command('installPackage(Modelica, "4.0.0", exactMatch=false)')
    send_omc_command('loadModel(Modelica)')
else:
    print('Modelica Standard Library already loaded.')

# %%
# Load the SMArtInt library using a path relative to the new CWD
model_path = os.path.join('..', 'SMArtInt', 'package.mo')
send_omc_command(f'loadFile("{model_path}")')
print('SMArtInt library loaded successfully.')

# %% [markdown]
# ## 2. Run the Simulation

# %%
model_to_simulate = 'SMArtInt.Tester.PipeHeatTransferExample.TFLite.TestPipe_tflite'
print(f'Simulating {model_to_simulate}...')
result = send_omc_command(f'simulate({model_to_simulate}, stopTime=1.0)')

# The result file path is relative to output_dir, so we construct the full path
result_filename = result.get('resultFile')
full_result_path = os.path.join(output_dir, result_filename) if result_filename else None

if full_result_path and os.path.exists(full_result_path):
    print(f'Simulation successful. Result file at: {full_result_path}')
else:
    print('Simulation failed.')
    full_result_path = None


# %% [markdown]
# ## 3. Plot Results using PyFMI

# %%
def plot_with_pyfmi(res_file, variables):
    if not res_file:
        print('No result file to plot.')
        return
    
    try:
        # Load the result file using the correct class
        res = ResultDymolaBinary(res_file)
        
        plt.figure(figsize=(12, 8))
        
        # Get trajectories for the specified variables
        for var in variables:
            try:
                trajectory = res.get_variable_data(var)
                plt.plot(trajectory.t, trajectory.x, label=var)
            except VariableNotFoundError:
                print(f'Variable not found in result file: {var}')
        
        plt.xlabel('Time (s)')
        plt.ylabel('Value')
        plt.title('Simulation Results')
        plt.legend()
        plt.grid(True)
        plt.show()
        
    except Exception as e:
        print(f'Failed to plot with PyFMI: {e}')

plot_vars = ['source.T', 'sink.T', 'source.m_flow']
plot_with_pyfmi(full_result_path, plot_vars)

