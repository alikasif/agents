import numpy as np

def quantize_16_to_4(data, axis=None):
    """
    Quantizes 16-bit floating point data to 4-bit integers (0-15).
    Uses linear asymmetric quantization.
    
    Args:
        data (np.ndarray): Input data in float16 or similar.
        axis (int, optional): Axis along which to calculate min/max. Defaults to None (global).
        
    Returns:
        quantized_data (np.ndarray): Data in uint8, scaled to 0-15.
        scale (float): Scale factor used.
        zero_point (int): Zero point used.
    """
    data = np.array(data, dtype=np.float32)
    
    # Identify min and max values
    f_min = np.min(data, axis=axis, keepdims=True)
    f_max = np.max(data, axis=axis, keepdims=True)
    
    # Calculate scale: (max - min) / (2^bits - 1)
    # 4 bits -> 15 levels
    scale = (f_max - f_min) / 15.0
    
    # Avoid division by zero if all values are identical
    scale = np.where(scale == 0, 1.0, scale)
    
    # Calculate zero point: round(q_min - f_min / scale)
    # q_min is 0 for uint4 range [0, 15]
    zero_point = np.round(-f_min / scale).astype(np.int32)
    zero_point = np.clip(zero_point, 0, 15)
    
    # Quantize: q = round(f / scale + zero_point)
    quantized_data = np.round(data / scale + zero_point).astype(np.int32)
    
    # Clip to 4-bit range [0, 15]
    quantized_data = np.clip(quantized_data, 0, 15).astype(np.uint8)
    
    return quantized_data, scale, zero_point

def dequantize_4_to_16(quantized_data, scale, zero_point):
    """
    Dequantizes 4-bit integers back to 16-bit floating point.
    
    Args:
        quantized_data (np.ndarray): Data in uint8 (0-15).
        scale (float): Scale factor.
        zero_point (int): Zero point.
        
    Returns:
        dequantized_data (np.ndarray): Recovered 16-bit data.
    """
    # f = (q - zero_point) * scale
    dequantized_data = (quantized_data.astype(np.float32) - zero_point) * scale
    return dequantized_data.astype(np.float16)
