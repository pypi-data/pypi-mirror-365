try:
    import tensorflow as tf
except ImportError as e:
    raise ImportError(
    "TensorFlow support is not available. "
    "Please install it with: pip install 'ano-optimizer[tensorflow]'"
    ) from e



class AnoTF(tf.keras.optimizers.Optimizer):
    def __init__(
        self,
        learning_rate=1e-4,
        beta_1=0.92,
        beta_2=0.99,
        weight_decay=0.0,
        epsilon=1e-8,
        logarithmic_schedule=False,
        name=None,
        **kwargs
    ):
        assert learning_rate > 0.0, "learning_rate must be positive"
        assert 0.0 <= beta_1 < 1.0 and 0.0 <= beta_2 < 1.0, "betas must be in [0,1)"
        assert weight_decay >= 0.0, "weight_decay must be non-negative"
        assert epsilon > 0.0, "epsilon must be positive"
        assert isinstance(logarithmic_schedule, bool), "logarithmic_schedule must be a boolean"
        
        if name is None:
            name = 'Ano' if logarithmic_schedule else 'Anolog'
        super().__init__(learning_rate=learning_rate, name=name, **kwargs)
        self.beta_1 = beta_1
        self.beta_2 = beta_2
        self.weight_decay = weight_decay
        self.epsilon = epsilon
        self.logarithmic_schedule = logarithmic_schedule
        
        self._m_weights = []
        self._v_weights = []
        self._variables_to_indices = {}

    def build(self, var_list):
        super().build(var_list)
        if hasattr(self, "_built") and self._built:
            return
        self._built = True

        self._m_weights = []
        self._v_weights = []
        for i, var in enumerate(var_list):
            self._m_weights.append(
                self.add_variable_from_reference(var, "exp_avg")
            )
            self._v_weights.append(
                self.add_variable_from_reference(var, "exp_avg_sq")
            )
            self._variables_to_indices[self._var_key(var)] = i

    def update_step(self, gradient, variable, learning_rate):
        lr = learning_rate

        beta_2 = tf.cast(self.beta_2, variable.dtype)
        epsilon = tf.cast(self.epsilon, variable.dtype)
        wd = tf.cast(self.weight_decay, variable.dtype)

        var_key = self._var_key(variable)
        index = self._variables_to_indices[var_key]
        
        m = self._m_weights[index]
        v = self._v_weights[index]

        step = tf.cast(self.iterations + 1, variable.dtype)
        step_int = tf.cast(self.iterations + 1, tf.int32)

        # β₁(t)
        if self.logarithmic_schedule:
            facteur_t = tf.maximum(step_int, 2)
            beta_1 = 1.0 - 1.0 / tf.math.log(tf.cast(facteur_t, tf.float32))
            beta_1 = tf.cast(beta_1, variable.dtype)
        else:
            beta_1 = tf.cast(self.beta_1, variable.dtype)

        bias_correction2 = 1.0 - tf.pow(beta_2, step)

        # m_t
        new_m = m * beta_1 + gradient * (1.0 - beta_1)

        # v_t
        square_grad = tf.square(gradient)
        sign_term = tf.sign(square_grad - v)
        new_v = v * beta_2 + sign_term * square_grad * (1.0 - beta_2)

        v_hat = new_v / bias_correction2
        adjusted_lr = lr / (tf.sqrt(v_hat) + epsilon)
        update = adjusted_lr * tf.abs(gradient) * tf.sign(new_m)

        if self.weight_decay > 0.0:
            variable.assign_sub(variable * lr * wd)

        variable.assign_sub(update)
        m.assign(new_m)
        v.assign(new_v)

    def get_config(self):
        config = super().get_config()
        config.update({
            "beta_2": self.beta_2,
            "weight_decay": self.weight_decay,
            "epsilon": self.epsilon,
        })
        return config
