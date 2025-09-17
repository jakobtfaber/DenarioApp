Here's a detailed breakdown of the methodology we'll use to carry out this research project. Your primary responsibility is to execute these steps carefully and document everything thoroughly.

**1. Data Generation & Simulation:**

*   **21cm Intensity Maps:** We'll start by generating a suite of 21cm intensity maps using a modified version of existing simulation codes (to be provided). These simulations will model the 21cm signal during the Epoch of Reionization (EoR) and Cosmic Dawn, incorporating different Early Dark Energy (EDE) scenarios.

    *   **EDE Parameter Space:** We will sample the EDE parameter space using a Latin Hypercube Sampling (LHS) method. The parameters to be varied are: `f_EDE` (the fraction of dark energy in the early universe), `z_c` (the critical redshift for the EDE transition), and `H0` (Hubble constant).
    *   We will generate N = 5000 simulations covering the following ranges:
        *   `f_EDE`: [0.0, 0.2]
        *   `z_c`: [3.0, 6.0]
        *   `H0`: [65, 75] km/s/Mpc
    *   **Simulation Volume & Resolution:** Each simulation will represent a comoving volume of (L = 200 Mpc/h)^3 with a grid resolution of N_grid = 256^3. This ensures sufficient dynamic range to capture the relevant scales of the 21cm signal.
    *   **Redshift Range:** The simulations will span a redshift range of z = 6 to z = 20, capturing the key epochs of Cosmic Dawn and EoR.

*   **Foreground Modeling:** Realistic foreground contamination is crucial. We will incorporate foreground models including:

    *   **Synchrotron Emission:** We will use a power-law model for synchrotron emission, with a spectral index that varies spatially.
    *   **Free-Free Emission:** We will model free-free emission as a function of frequency and electron temperature.
    *   **Point Sources:** We will randomly distribute point sources across the sky, with flux densities drawn from a power-law distribution.
    *   **Foreground Amplitude:** The foreground amplitude will be set to be approximately 10 times the signal at the EoR frequencies.

*   **Instrumental Effects:** We will simulate instrumental effects by:

    *   **Adding Gaussian Noise:** We will add Gaussian noise to the simulated maps, with a standard deviation that depends on the observing time and system temperature.
    *   **Beam Smoothing:** We will convolve the maps with a Gaussian beam representing the telescope's point spread function. The beam size will be frequency-dependent.

**2. Wavelet Scattering Network (WSN) Feature Extraction:**

*   **WSN Architecture:** We will use a pre-existing WSN implementation (e.g., from the `scatnet` library in Python). The WSN architecture will consist of:
    *   **Number of Layers:** 2 scattering layers.
    *   **Wavelet Type:** Morlet wavelets.
    *   **Scales per Octave:** 8 scales per octave.
    *   **Pooling Size:** 4x4 average pooling after each scattering layer.
*   **Preprocessing:** Before feeding the 21cm maps to the WSN, we will:
    *   **Normalize:** Normalize each map to have zero mean and unit variance. This ensures that the WSN is not sensitive to the overall amplitude of the signal.
    *   **Resize:** Resize the 256x256 images to 128x128 to reduce computational cost.
*   **Feature Extraction:** The WSN will transform each 21cm intensity map into a low-dimensional feature vector. The output of the WSN will be a vector of scattering coefficients.
    *   **Dimensionality Reduction:** The WSN will reduce the dimensionality of the data from 256x256 pixels to a feature vector of length approximately 500.
*   **Data Organization:** We will organize the extracted features into a matrix X, where each row corresponds to a 21cm map and each column corresponds to a scattering coefficient. We will also create a vector y containing the corresponding EDE parameters for each map.

**3. Machine Learning Model Training & Validation:**

*   **Model Selection:** We will use Gaussian Process Regression (GPR) as our machine learning model. GPR is a non-parametric model that provides uncertainty estimates, which are crucial for cosmological parameter inference.

*   **Training & Validation Split:** We will split the data into training and validation sets using an 80/20 split. This means that 80% of the data will be used to train the GPR model, and 20% of the data will be used to evaluate its performance. The split will be performed randomly, but we will ensure that the training and validation sets have similar distributions of EDE parameters.

*   **GPR Kernel:** We will use a Radial Basis Function (RBF) kernel for the GPR model. The RBF kernel is a common choice for regression problems and has a single hyperparameter, the length scale, which controls the smoothness of the model.

*   **Hyperparameter Optimization:** We will optimize the hyperparameters of the GPR model using a gradient-based optimization algorithm. Specifically, we will use the L-BFGS-B algorithm to maximize the marginal log-likelihood of the training data.

*   **Performance Evaluation:** We will evaluate the performance of the GPR model on the validation set using the following metrics:

    *   **Root Mean Squared Error (RMSE):** This measures the average difference between the predicted EDE parameters and the true EDE parameters.
    *   **R-squared (R^2):** This measures the proportion of variance in the EDE parameters that is explained by the GPR model.
    *   **Calibration Score:** This measures the agreement between the predicted uncertainties and the true errors.

**4. Inference and Uncertainty Quantification:**

*   **Parameter Inference:** Once the GPR model is trained and validated, we can use it to infer EDE parameters from new 21cm intensity maps.

*   **Uncertainty Quantification:** The GPR model provides uncertainty estimates for its predictions. These uncertainty estimates can be used to quantify the uncertainty in the inferred EDE parameters.

*   **Posterior Distribution:** The output of the GPR model is a Gaussian distribution over the EDE parameters. This distribution represents the posterior distribution, which is the probability distribution of the EDE parameters given the observed 21cm intensity map.

*   **Marginalization:** We can marginalize the posterior distribution over nuisance parameters (e.g., foreground parameters) to obtain the marginalized posterior distribution for the EDE parameters.

**5. Exploratory Data Analysis (EDA):**

Before diving into the full analysis, we'll perform some EDA to understand the characteristics of our simulated data:

*   **Summary Statistics:** We'll calculate basic summary statistics for the EDE parameters and the simulated 21cm intensity maps.
    *   For EDE parameters (`f_EDE`, `z_c`, `H0`): Minimum, Maximum, Mean, Median, Standard Deviation, Quantiles (25th, 50th, 75th). For example:

        | Parameter | Min  | Max  | Mean | Median | Std Dev | 25th Quantile | 75th Quantile |
        | --------- | ---- | ---- | ---- | ------ | ------- | ------------- | ------------- |
        | `f_EDE`   | 0.0  | 0.2  | 0.1  | 0.1    | 0.058   | 0.05          | 0.15          |
        | `z_c`     | 3.0  | 6.0  | 4.5  | 4.5    | 0.866   | 3.75          | 5.25          |
        | `H0`      | 65   | 75   | 70   | 70     | 2.887   | 67.5          | 72.5          |

    *   For 21cm intensity maps (for a subset of simulations to get a sense of the distribution): Mean, Standard Deviation, Minimum, Maximum pixel values across the map.

*   **Correlation Analysis:** We'll examine the correlation between different EDE parameters. This will help us understand if there are any degeneracies between the parameters. We'll compute the Pearson correlation coefficient between each pair of EDE parameters.
    *   Example Correlation Matrix:

        |         | `f_EDE` | `z_c` | `H0` |
        | ------- | ------- | ----- | ---- |
        | `f_EDE` | 1.0     | 0.1   | -0.2 |
        | `z_c`   | 0.1     | 1.0   | 0.05 |
        | `H0`    | -0.2    | 0.05  | 1.0  |

*   **Signal-to-Noise Ratio (SNR):** We'll estimate the SNR of the 21cm signal in the simulated maps, both before and after adding foregrounds and instrumental noise. This will give us an idea of how challenging it will be to extract information from the data. We can compute the SNR as the ratio of the standard deviation of the 21cm signal to the standard deviation of the noise.

**Important Notes:**

*   Document every step meticulously. Keep track of all parameters used in the simulations, WSN, and GPR model.
*   Version control your code using Git.
*   Use a consistent naming convention for all files and variables.
*   Write clear and concise comments in your code.
*   Regularly back up your data and code.
\