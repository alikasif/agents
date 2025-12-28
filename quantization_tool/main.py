import numpy as np
from quantizer import quantize_16_to_4, dequantize_4_to_16

def main():
    print("--- 16-bit to 4-bit Quantization Demo ---")
    
    # 1. Generate sample 16-bit data (float16)
    np.random.seed(42)
    original_data = np.random.uniform(-10, 10, size=(10,)).astype(np.float16)
    print(f"\nOriginal Data (float16):\n{original_data}")
    
    # 2. Quantize to 4-bit
    quantized, scale, zp = quantize_16_to_4(original_data)
    print(f"\nQuantized Data (4-bit, range 0-15):\n{quantized}")
    print(f"Scale: {scale.flatten()[0]:.4f}, Zero Point: {zp.flatten()[0]}")
    
    # 3. Dequantize back to 16-bit
    reconstructed = dequantize_4_to_16(quantized, scale, zp)
    print(f"\nReconstructed Data (float16):\n{reconstructed}")
    
    # 4. Calculate Error
    mse = np.mean((original_data.astype(np.float32) - reconstructed.astype(np.float32))**2)
    print(f"\nMean Squared Error (MSE): {mse:.6f}")
    
    # 5. Visual Check
    print("\nComparison (Original vs Reconstructed):")
    for o, r in zip(original_data, reconstructed):
        print(f"Original: {o:8.4f} | Reconstructed: {r:8.4f} | Diff: {abs(o-r):8.4f}")

if __name__ == "__main__":
    main()
