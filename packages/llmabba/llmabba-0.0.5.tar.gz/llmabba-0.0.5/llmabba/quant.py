import numpy as np
import warnings 

def rd_func(x):
    return np.round(x, decimals=0)
    


def clip_func(x, a_min, a_max):
    return np.clip(x, a_min=a_min, a_max=a_max)


    
class QUANT():
    """
    Parameters
    ----------
    bits : int, default=8
        The bitwidth of integer format, the larger it is, the wider range the quantized value can be.
        
    sign : bool, default=1
        Whether or not to quantize the value to symmetric integer range.
    
    zpoint : bool, default=1
        Whether or not to compute the zero point. If `zpoint=0`, then the quantized range must be symmetric.
        
    rd_func : function, default=None
        The rounding function used for the quantization. The default is round to nearest.
        
    clip_range : list, default=None
        The clipping function for the quantization.
        
    epsilon : double, default=1e-12
        When the x is comprised of single value, then the scaling factor will be (b - a + epsilon) / (alpha - beta)
        for mapping [a, b] to [alpha, beta].
        
    Methods
    ----------
    quant(x):
        Method that quantize ``x`` to the user-specific arithmetic format.
        
    """
    def __init__(self, bits=8, sign=1, zpoint=1, rd_func=None, clip_range=None, epsilon=1e-12):
        self.bits = bits
        self.sign = sign
        self.zpoint = zpoint
        
        self.clip_range = clip_range
        self.epsilon = epsilon 
        
        if bits in {8, 16, 32, 64}:
            if bits == 8:
                self.intType = np.int8
                
            elif bits == 16:
                self.intType = np.int16
                
            elif bits == 32:
                self.intType = np.int32
                
            elif bits == 64:
                self.intType = np.int64
                
        else:
            warnings.warn("Current int type not support this bitwidth, use int64 to simulate.")
            self.intType = np.int64
        
        if self.sign == 1:
            if self.zpoint == 1:
                self.alpha_q = -2**(self.bits - 1)
                self.beta_q = 2**(self.bits - 1) - 1
            else:
                self.beta_q = 2**(self.bits - 1) - 1
                self.alpha_q = -self.beta_q
                
        else:
            if self.zpoint == 0:
                self.beta_q = 2**(self.bits - 1) - 1
                self.alpha_q = -self.beta_q
            else:
                raise ValueError('Please set `zpoint` to 0.')
        
            
            
    def __call__(self, x):
        x_min = np.min(x)
        x_max = np.max(x)
        
        if self.sign != 1:
            abs_max = max(abs(x_min), abs(x_max))
            x_min = -abs_max
            x_max = abs_max
            
        self.scaling, self.zpoint = self.compute_scaling(x_min, x_max, self.alpha_q, self.beta_q)
        
        try:
            x_q = self.quantization(x, self.scaling, self.zpoint)
        except:
            self.scaling, self.zpoint = self.compute_scaling(x_min, x_max+self.epsilon, self.alpha_q, self.beta_q)
            x_q = self.quantization(x, self.scaling, self.zpoint)
            
        return x_q
        
    def dequant(self, x_q):
        return self.dequantization(x_q, self.scaling, self.zpoint)
        
    def quantization(self, x, s, z):
        x_q = rd_func((x - z)/s)
            
        if self.clip_range is None:
            x_q = self.intType(clip_func(x_q, a_min=self.alpha_q, a_max=self.beta_q))
        else:
            x_q = self.intType(clip_func(x_q, a_min=self.clip_range[0], a_max=self.beta_q[self.clip_range[1]]))
        
        return x_q

    def dequantization(self, x_q, s, z):
        x_q = x_q.astype(np.float32)
        x = s * x_q + z
        return x

    def compute_scaling(self, alpha, beta, alpha_q, beta_q):
        s = (beta - alpha) / (beta_q - alpha_q)
        z = (alpha * beta_q - beta * alpha_q) / (beta_q - alpha_q)

        return s, z
    