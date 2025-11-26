// Auto-generated scaler parameters
// StandardScaler: scaled = (x - mean) / scale

#ifndef SCALER_PARAMS_H
#define SCALER_PARAMS_H

#define N_FEATURES 22

const float SCALER_MEAN[N_FEATURES] = {
    0.98310267f,  // f0
    0.01344694f,  // f1
    0.00331132f,  // f2
    0.00013907f,  // f3
    37.25777055f,  // f4
    0.45649920f,  // f5
    23.22001498f,  // f6
    0.00479160f,  // f7
    0.02021610f,  // f8
    0.00000028f,  // f9
    3.94390001f,  // f10
    2.16273576f,  // f11
    110.46743201f,  // f12
    0.10785737f,  // f13
    12432.94574528f,  // f14
    0.32302424f,  // f15
    0.00000000f,  // f16
    0.00000000f,  // f17
    78.45908637f,  // f18
    0.00000000f,  // f19
    0.00000000f,  // f20
    0.00000000f  // f21
};

const float SCALER_SCALE[N_FEATURES] = {
    0.12888682f,  // f0
    0.11517864f,  // f1
    0.05744875f,  // f2
    0.01179192f,  // f3
    49.75819181f,  // f4
    1.47126715f,  // f5
    153.38845091f,  // f6
    0.06905534f,  // f7
    0.14073879f,  // f8
    0.00052503f,  // f9
    0.49789058f,  // f10
    0.50973948f,  // f11
    37.80937948f,  // f12
    0.31020019f,  // f13
    28108.88553363f,  // f14
    0.46763189f,  // f15
    1.00000000f,  // f16
    1.00000000f,  // f17
    71.07747217f,  // f18
    1.00000000f,  // f19
    1.00000000f,  // f20
    1.00000000f  // f21
};

// Apply StandardScaler to feature vector
void scale_features(float features[N_FEATURES]) {
    for (int i = 0; i < N_FEATURES; i++) {
        features[i] = (features[i] - SCALER_MEAN[i]) / SCALER_SCALE[i];
    }
}

#endif // SCALER_PARAMS_H
