try:
    import torch
except ImportError:
    raise ImportError("Torch backend is not installed. Please reinstall 'ano-optimizer' or install 'torch', separately.")

try:
    import math
except ImportError:
    raise ImportError("Math module is not available. Please ensure Python's standard library is intact.")

class Ano(torch.optim.Optimizer):
    def __init__(self, params, lr:float=1e-4, betas:tuple=(0.92, 0.99), weight_decay:float=0e-2, eps:float=1e-8, logarithmic_schedule:bool=False):
        if lr <= 0.0:
            raise ValueError("lr must be positive")
        if not 0.0 <= betas[0] < 1.0 or not 0.0 <= betas[1] < 1.0:
            raise ValueError("betas must be in [0,1)")
        defaults = dict(lr=lr, betas=betas,
                        weight_decay=weight_decay, eps=eps)
        self.logarithmic_schedule = logarithmic_schedule
        self.__name__ = 'Ano' if logarithmic_schedule else 'Anolog'
        super().__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None):
        """
        Performs a single optimization step.
        """
        loss = closure() if closure is not None else None

        for group in self.param_groups:
            beta1, beta2 = group["betas"]
            lr, wd, eps = group["lr"], group["weight_decay"], group["eps"]

            for p in group['params']:
                if p.grad is None:
                    continue

                g = p.grad.data

                if g.is_sparse:
                    raise RuntimeError("Ano does not support sparse gradients")
                
                # Get or initialize momentum
                state = self.state[p]
                # State initialisation
                if len(state) == 0:
                    state["step"] = 0
                    state["exp_avg"] = torch.zeros_like(p)
                    state["exp_avg_sq"] = torch.zeros_like(p)
                    
                exp_avg, exp_avg_sq = state["exp_avg"], state["exp_avg_sq"]
                
                state["step"] += 1
                t = state["step"]
                
                if self.logarithmic_schedule:
                    # Anolog beta1 = 1 - 1 / log(k)
                    max_t = max(2, t)
                    beta1 = 1 - 1 / math.log(max_t)
                    
                if t > 0:
                    # Bias-corrected coeffs
                    bias_c2 = 1 - beta2 ** t
                    
                    # m_k
                    exp_avg.mul_(beta1).add_(g, alpha=1 - beta1)
                    
                    square_grad = torch.square(g)
                    sign_term = torch.sign(square_grad - state['exp_avg_sq'])
                    state['exp_avg_sq'].mul_(beta2).add_(sign_term * square_grad, alpha=1 - beta2)
                        
                    # Correction du biais
                    v_hat = exp_avg_sq / bias_c2

                    adjusted_learning_rate = lr / torch.sqrt(v_hat + eps)

                    update = adjusted_learning_rate * g.abs() * torch.sign(exp_avg)

                    # Decoupled weight-decay
                    if wd != 0.0:
                        p.mul_(1 - lr * wd)
                        
                    # Update parameters with sign of momentum
                    p.add_(-update)
        return loss
