#!/usr/bin/env python3
"""
MLP(8) modelini ve StandardScaler parametrelerini C array'lerine export eder.
ESP8266'da kullanılmak üzere .h header dosyaları oluşturur.
"""
import pickle
import numpy as np


def export_scaler_to_c(scaler, output_file):
    """
    StandardScaler parametrelerini C header dosyasına yaz.
    """
    mean = scaler.mean_
    scale = scaler.scale_  # std
    n_features = len(mean)

    with open(output_file, 'w') as f:
        f.write("// Auto-generated scaler parameters\n")
        f.write("// StandardScaler: scaled = (x - mean) / scale\n\n")
        f.write("#ifndef SCALER_PARAMS_H\n")
        f.write("#define SCALER_PARAMS_H\n\n")
        
        f.write(f"#define N_FEATURES {n_features}\n\n")
        
        # Mean array
        f.write("const float SCALER_MEAN[N_FEATURES] = {\n")
        for i, val in enumerate(mean):
            f.write(f"    {val:.8f}f")
            if i < len(mean) - 1:
                f.write(",")
            f.write(f"  // f{i}\n")
        f.write("};\n\n")
        
        # Scale (std) array
        f.write("const float SCALER_SCALE[N_FEATURES] = {\n")
        for i, val in enumerate(scale):
            f.write(f"    {val:.8f}f")
            if i < len(scale) - 1:
                f.write(",")
            f.write(f"  // f{i}\n")
        f.write("};\n\n")
        
        # Scaling function
        f.write("// Apply StandardScaler to feature vector\n")
        f.write("void scale_features(float features[N_FEATURES]) {\n")
        f.write("    for (int i = 0; i < N_FEATURES; i++) {\n")
        f.write("        features[i] = (features[i] - SCALER_MEAN[i]) / SCALER_SCALE[i];\n")
        f.write("    }\n")
        f.write("}\n\n")
        
        f.write("#endif // SCALER_PARAMS_H\n")
    
    print(f"[+] Scaler parameters exported to: {output_file}")


def export_mlp_to_c(model, output_file):
    """
    MLPClassifier modelini C header dosyasına yaz.
    Mimari: Input(22) -> Hidden(8, ReLU) -> Output(1, Sigmoid)
    """
    # Model ağırlıkları ve bias'ları al
    weights_input_hidden = model.coefs_[0]  # shape: (22, 8)
    bias_hidden = model.intercepts_[0]      # shape: (8,)
    weights_hidden_output = model.coefs_[1] # shape: (8, 1)
    bias_output = model.intercepts_[1]      # shape: (1,)
    
    n_input = weights_input_hidden.shape[0]
    n_hidden = weights_input_hidden.shape[1]
    n_output = weights_hidden_output.shape[1]
    
    with open(output_file, 'w') as f:
        f.write("// Auto-generated MLP(8) model weights\n")
        f.write("// Architecture: Input(22) -> Hidden(8, ReLU) -> Output(1, Sigmoid)\n\n")
        f.write("#ifndef MODEL_WEIGHTS_H\n")
        f.write("#define MODEL_WEIGHTS_H\n\n")
        f.write("#include <math.h>\n\n")
        
        f.write(f"#define N_INPUT {n_input}\n")
        f.write(f"#define N_HIDDEN {n_hidden}\n")
        f.write(f"#define N_OUTPUT {n_output}\n\n")
        
        # Input -> Hidden weights (22x8 = 176 values)
        f.write("// Weights: Input -> Hidden (22x8)\n")
        f.write("const float W_INPUT_HIDDEN[N_INPUT][N_HIDDEN] = {\n")
        for i in range(n_input):
            f.write("    {")
            for j in range(n_hidden):
                f.write(f"{weights_input_hidden[i, j]:.8f}f")
                if j < n_hidden - 1:
                    f.write(", ")
            f.write("}")
            if i < n_input - 1:
                f.write(",")
            f.write(f"  // f{i}\n")
        f.write("};\n\n")
        
        # Hidden bias (8 values)
        f.write("// Bias: Hidden layer (8)\n")
        f.write("const float B_HIDDEN[N_HIDDEN] = {\n")
        for i, val in enumerate(bias_hidden):
            f.write(f"    {val:.8f}f")
            if i < len(bias_hidden) - 1:
                f.write(",")
            f.write(f"  // h{i}\n")
        f.write("};\n\n")
        
        # Hidden -> Output weights (8x1 = 8 values)
        f.write("// Weights: Hidden -> Output (8x1)\n")
        f.write("const float W_HIDDEN_OUTPUT[N_HIDDEN][N_OUTPUT] = {\n")
        for i in range(n_hidden):
            f.write("    {")
            for j in range(n_output):
                f.write(f"{weights_hidden_output[i, j]:.8f}f")
                if j < n_output - 1:
                    f.write(", ")
            f.write("}")
            if i < n_hidden - 1:
                f.write(",")
            f.write(f"  // h{i}\n")
        f.write("};\n\n")
        
        # Output bias (1 value)
        f.write("// Bias: Output layer (1)\n")
        f.write("const float B_OUTPUT[N_OUTPUT] = {\n")
        for i, val in enumerate(bias_output):
            f.write(f"    {val:.8f}f")
            if i < len(bias_output) - 1:
                f.write(",")
            f.write("\n")
        f.write("};\n\n")
        
        # Activation functions
        f.write("// ReLU activation function\n")
        f.write("inline float relu(float x) {\n")
        f.write("    return (x > 0.0f) ? x : 0.0f;\n")
        f.write("}\n\n")
        
        f.write("// Sigmoid activation function\n")
        f.write("inline float sigmoid(float x) {\n")
        f.write("    return 1.0f / (1.0f + expf(-x));\n")
        f.write("}\n\n")
        
        # Inference function
        f.write("// MLP inference function\n")
        f.write("// Input: scaled features[22]\n")
        f.write("// Output: probability [0.0, 1.0] (>0.5 = malicious)\n")
        f.write("float mlp_inference(const float features[N_INPUT]) {\n")
        f.write("    float hidden[N_HIDDEN];\n")
        f.write("    float output;\n\n")
        
        f.write("    // Layer 1: Input -> Hidden (with ReLU)\n")
        f.write("    for (int h = 0; h < N_HIDDEN; h++) {\n")
        f.write("        float sum = B_HIDDEN[h];\n")
        f.write("        for (int i = 0; i < N_INPUT; i++) {\n")
        f.write("            sum += features[i] * W_INPUT_HIDDEN[i][h];\n")
        f.write("        }\n")
        f.write("        hidden[h] = relu(sum);\n")
        f.write("    }\n\n")
        
        f.write("    // Layer 2: Hidden -> Output (with Sigmoid)\n")
        f.write("    output = B_OUTPUT[0];\n")
        f.write("    for (int h = 0; h < N_HIDDEN; h++) {\n")
        f.write("        output += hidden[h] * W_HIDDEN_OUTPUT[h][0];\n")
        f.write("    }\n")
        f.write("    output = sigmoid(output);\n\n")
        
        f.write("    return output;\n")
        f.write("}\n\n")
        
        # Classification function
        f.write("// Classify request: 0=benign, 1=malicious\n")
        f.write("int classify_request(const float features[N_INPUT], float threshold=0.5f) {\n")
        f.write("    float prob = mlp_inference(features);\n")
        f.write("    return (prob >= threshold) ? 1 : 0;\n")
        f.write("}\n\n")
        
        f.write("#endif // MODEL_WEIGHTS_H\n")
    
    print(f"[+] Model weights exported to: {output_file}")
    
    # Model istatistikleri
    total_params = (n_input * n_hidden + n_hidden + 
                   n_hidden * n_output + n_output)
    total_bytes = total_params * 4  # float32
    
    print(f"\n[*] Model Statistics:")
    print(f"    Architecture: {n_input} -> {n_hidden} -> {n_output}")
    print(f"    Total parameters: {total_params}")
    print(f"    Memory (float32): {total_bytes} bytes (~{total_bytes/1024:.2f} KB)")


def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    print("[*] Loading trained model and scaler...")
    
    # Model ve scaler'ı yükle
    model_path = os.path.join(script_dir, "best_model.pkl")
    scaler_path = os.path.join(script_dir, "scaler.pkl")
    
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    
    print("[+] Model and scaler loaded successfully")
    print(f"    Model type: {type(model).__name__}")
    print(f"    Scaler type: {type(scaler).__name__}")
    
    # Export
    firmware_dir = os.path.join(project_dir, "esp8266_firmware")
    os.makedirs(firmware_dir, exist_ok=True)
    
    print("\n[*] Exporting scaler parameters...")
    export_scaler_to_c(scaler, os.path.join(firmware_dir, "scaler_params.h"))
    
    print("\n[*] Exporting model weights...")
    export_mlp_to_c(model, os.path.join(firmware_dir, "model_weights.h"))
    
    print("\n" + "="*60)
    print("✅ Export complete!")
    print("="*60)
    print("\nGenerated files:")
    print("  - scaler_params.h   (feature scaling)")
    print("  - model_weights.h   (MLP inference)")
    print("\nNext steps:")
    print("  1. Copy these .h files to your ESP8266 project")
    print("  2. Include them in your Arduino sketch")
    print("  3. Use scale_features() and mlp_inference() functions")


if __name__ == "__main__":
    main()
