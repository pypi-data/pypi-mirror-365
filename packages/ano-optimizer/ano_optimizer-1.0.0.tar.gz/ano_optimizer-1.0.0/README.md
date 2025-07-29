# Ano Optimizer

**Ano** is the official implementation of the optimizer introduced in the paper  
**["Ano: Faster is Better in Noisy Landscapes"](https://doi.org/10.5281/zenodo.16422081)**

This optimizer is designed for efficient and stable training in high-variance regimes, and includes both a standard and a logarithmic-scheduled variant (Anolog). Native support is provided for both **PyTorch** and **TensorFlow**.

---

## Key Features

- **Sign–Magnitude Decoupling**  
  Ano separates update direction and magnitude, using the sign of the momentum and the norm of the raw gradient respectively. This improves stability and performance in high-variance settings.

- **Additive Second-Moment Estimation**  
  Ano employs an additive second-moment update, inspired by Yogi, to ensure smoother convergence and mitigate issues with gradient sparsity.

- **Logarithmic Momentum Schedule (Anolog)**  
  A variant of Ano using a time-dependent momentum parameter, enabled via `logarithmic_schedule=True`. This extension improves noise attenuation in stationary training regimes.

- **Dual Framework Support**  
  Compatible with both PyTorch and TensorFlow. Import the appropriate implementation via `ano_optimizer.Ano` or `ano_optimizer.tensorflow.AnoTF`.

---

## Installation

Install the PyTorch version (default):

```bash
pip install ano-optimizer
```

Install with TensorFlow support:

```bash
pip install 'ano-optimizer[tensorflow]'
```

---

## Usage

### PyTorch

```python
from ano_optimizer import Ano  
import torch

model = MyModel()  
optimizer = Ano(model.parameters(), lr=1e-4)

for input, target in data_loader:  
    optimizer.zero_grad()  
    output = model(input)  
    loss = loss_fn(output, target)  
    loss.backward()  
    optimizer.step()
```

To enable Anolog:

```python
optimizer = Ano(model.parameters(), lr=1e-4, logarithmic_schedule=True)
```

---

### TensorFlow

```python
from ano_optimizer.tensorflow import AnoTF  
import tensorflow as tf

model = MyModel()  
optimizer = AnoTF(learning_rate=1e-4)

with tf.GradientTape() as tape:  
    predictions = model(inputs)  
    loss = loss_fn(targets, predictions)

gradients = tape.gradient(loss, model.trainable_variables)  
optimizer.apply_gradients(zip(gradients, model.trainable_variables))
```

To enable Anolog:

```python
optimizer = AnoTF(learning_rate=1e-4, logarithmic_schedule=True)
```

---

## Citation

If you use this work in your research, please cite the following paper:

```plaintext
@misc{kegreisz2025ano,
  author       = {Kegreisz, Adrien},
  title        = {Ano: Faster is Better in Noisy Landscapes},
  year         = {2025},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.16422081},
  url          = {https://doi.org/10.5281/zenodo.16422081}
}
```

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contributing

Contributions, issues, and suggestions are welcome. Please open an issue or submit a pull request.
