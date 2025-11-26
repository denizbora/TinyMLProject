// Auto-generated MLP(8) model weights
// Architecture: Input(22) -> Hidden(8, ReLU) -> Output(1, Sigmoid)

#ifndef MODEL_WEIGHTS_H
#define MODEL_WEIGHTS_H

#include <math.h>

#define N_INPUT 22
#define N_HIDDEN 8
#define N_OUTPUT 1

// Weights: Input -> Hidden (22x8)
const float W_INPUT_HIDDEN[N_INPUT][N_HIDDEN] = {
    {-0.02580648f, 0.00000000f, -0.00000000f, -0.13380486f, -0.02615760f, -0.01911464f, -0.02152441f, 0.00708626f},  // f0
    {0.05277428f, -0.00000000f, -0.00000000f, 0.06032659f, 0.05328036f, 0.04236865f, 0.04623181f, -0.03705439f},  // f1
    {0.03849424f, 0.00000000f, 0.00000000f, 0.04409964f, 0.03909504f, 0.02190317f, 0.02990477f, -0.01920984f},  // f2
    {0.00595027f, -0.00000000f, -0.00000000f, 0.02114522f, 0.00592134f, 0.00617592f, 0.00602812f, -0.00274485f},  // f3
    {0.05910762f, -0.00000000f, -0.00000000f, 0.09971938f, 0.05906010f, 0.04451283f, 0.04761006f, 0.01340769f},  // f4
    {-0.15758881f, 0.00000000f, 0.00000000f, 0.20426787f, -0.16075350f, -0.05850599f, -0.11158283f, 0.05441163f},  // f5
    {-0.00667709f, 0.00000000f, 0.00000000f, 0.16598302f, -0.00649620f, -0.00280003f, -0.01308896f, 0.00266538f},  // f6
    {-0.36828470f, -0.00000000f, 0.00000000f, 0.69547004f, -0.37579054f, -0.12780695f, -0.25795749f, 0.18690816f},  // f7
    {-0.66304809f, -0.00000000f, 0.00000000f, 1.07773876f, -0.67584515f, -0.28017113f, -0.48642433f, 0.33792308f},  // f8
    {-0.03174516f, -0.00000000f, -0.00000000f, -0.00009279f, -0.03174482f, -0.03176426f, -0.03175100f, 0.03173858f},  // f9
    {0.07508217f, -0.00000000f, 0.00000000f, 0.01188201f, 0.07707508f, 0.02191169f, 0.04348412f, -0.01375682f},  // f10
    {0.18548061f, 0.00000000f, 0.00000000f, 0.15452723f, 0.18689314f, 0.14027824f, 0.15980206f, -0.08753844f},  // f11
    {0.10626505f, 0.00000000f, 0.00000000f, 0.06432641f, 0.10716936f, 0.07312536f, 0.10202921f, 0.01104577f},  // f12
    {0.00026963f, -0.00000000f, 0.00000000f, 0.20311916f, -0.00050656f, 0.02890697f, 0.01427433f, 0.02218747f},  // f13
    {0.06330443f, -0.00000000f, 0.00000000f, 0.06688815f, 0.06354813f, 0.05267796f, 0.06138346f, 0.00401171f},  // f14
    {0.21213293f, -0.00000000f, -0.00000000f, -0.01944905f, 0.21516028f, 0.07936237f, 0.15124947f, 0.04215803f},  // f15
    {-0.00000000f, -0.00000000f, 0.00000000f, 0.00000000f, 0.00000000f, 0.00000000f, -0.00000000f, -0.00000000f},  // f16
    {0.00000000f, 0.00000000f, 0.00000000f, -0.00000000f, -0.00000000f, -0.00000000f, 0.00000000f, -0.00000000f},  // f17
    {0.03569849f, 0.00000000f, 0.00000000f, 0.16383298f, 0.03481509f, 0.06993843f, 0.05449110f, -0.09321775f},  // f18
    {-0.00000000f, 0.00000000f, 0.00000000f, -0.00000000f, 0.00000000f, 0.00000000f, -0.00000000f, -0.00000000f},  // f19
    {-0.00000000f, 0.00000000f, 0.00000000f, -0.00000000f, 0.00000000f, 0.00000000f, -0.00000000f, 0.00000000f},  // f20
    {0.00000000f, -0.00000000f, 0.00000000f, 0.00000000f, 0.00000000f, -0.00000000f, 0.00000000f, -0.00000000f}  // f21
};

// Bias: Hidden layer (8)
const float B_HIDDEN[N_HIDDEN] = {
    5.37964964f,  // h0
    -0.06654064f,  // h1
    -0.06352766f,  // h2
    0.07770199f,  // h3
    5.46953344f,  // h4
    3.06691599f,  // h5
    4.16657019f,  // h6
    0.23368287f  // h7
};

// Weights: Hidden -> Output (8x1)
const float W_HIDDEN_OUTPUT[N_HIDDEN][N_OUTPUT] = {
    {-0.90135580f},  // h0
    {0.00000000f},  // h1
    {0.00000000f},  // h2
    {1.22498047f},  // h3
    {-0.92243838f},  // h4
    {-0.27609110f},  // h5
    {-0.59740412f},  // h6
    {0.45141309f}  // h7
};

// Bias: Output layer (1)
const float B_OUTPUT[N_OUTPUT] = {
    0.00551107f
};

// ReLU activation function
inline float relu(float x) {
    return (x > 0.0f) ? x : 0.0f;
}

// Sigmoid activation function
inline float sigmoid(float x) {
    return 1.0f / (1.0f + expf(-x));
}

// MLP inference function
// Input: scaled features[22]
// Output: probability [0.0, 1.0] (>0.5 = malicious)
float mlp_inference(const float features[N_INPUT]) {
    float hidden[N_HIDDEN];
    float output;

    // Layer 1: Input -> Hidden (with ReLU)
    for (int h = 0; h < N_HIDDEN; h++) {
        float sum = B_HIDDEN[h];
        for (int i = 0; i < N_INPUT; i++) {
            sum += features[i] * W_INPUT_HIDDEN[i][h];
        }
        hidden[h] = relu(sum);
    }

    // Layer 2: Hidden -> Output (with Sigmoid)
    output = B_OUTPUT[0];
    for (int h = 0; h < N_HIDDEN; h++) {
        output += hidden[h] * W_HIDDEN_OUTPUT[h][0];
    }
    output = sigmoid(output);

    return output;
}

// Classify request: 0=benign, 1=malicious
int classify_request(const float features[N_INPUT], float threshold=0.5f) {
    float prob = mlp_inference(features);
    return (prob >= threshold) ? 1 : 0;
}

#endif // MODEL_WEIGHTS_H
