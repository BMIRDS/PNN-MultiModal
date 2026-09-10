# PNN-MultiModal: Multimodal Deep Learning for Brain Tumor-Related Epilepsy Prediction

Multimodal deep learning framework integrating multiplex immunofluorescence imaging, spatial transcriptomics, and clinical metadata for prediction of brain tumor-related epilepsy in glioma.

## Overview

PNN-MultiModal is a comprehensive deep learning framework designed to predict brain tumor-related epilepsy (BTE) in glioma patients by integrating three complementary data modalities:

- **Multiplex Immunofluorescence (mIF) Imaging**: High-dimensional spatial protein expression data capturing the tumor microenvironment composition
- **Spatial Transcriptomics**: Gene expression patterns with preserved spatial context within tumor regions
- **Clinical Metadata**: Patient demographics, tumor characteristics, and clinical outcomes

This framework leverages state-of-the-art deep learning techniques to uncover the complex interactions between immune infiltration, molecular profiles, and clinical manifestations of seizure risk [...]

## Key Features

- **Multimodal Integration**: Seamlessly combines imaging, genomic, and clinical data
- **Spatial Context Preservation**: Maintains spatial relationships crucial for understanding tumor microenvironment
- **Interpretability**: Provides insights into which modalities and features drive epilepsy prediction
- **End-to-End Pipeline**: From data preprocessing to model evaluation and validation
- **Reproducible Research**: Comprehensive notebooks and documentation for full transparency

## Project Structure

```
PNN-MultiModal/
├── README.md                 # This file
├── notebooks/                # Jupyter notebooks for analysis and experiments
│   ├── data_exploration.ipynb
│   ├── preprocessing.ipynb
│   ├── model_training.ipynb
│   └── evaluation.ipynb
├── src/                      # Python source code
│   ├── models/              # Deep learning model architectures
│   ├── data/                # Data loading and preprocessing utilities
│   ├── utils/               # Helper functions and utilities
│   └── evaluation/          # Evaluation metrics and visualization
├── data/                    # Data directory (not included in repo)
├── results/                 # Output directory for model results
└── requirements.txt         # Python dependencies
```

## Technical Stack

- **Deep Learning**: PyTorch / TensorFlow
- **Data Processing**: NumPy, Pandas, SciPy
- **Image Analysis**: scikit-image, OpenCV
- **Spatial Analysis**: Scanpy, Squidpy (for spatial transcriptomics)
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Development**: Jupyter Notebook, Python 3.8+

## Getting Started

### Prerequisites

- Python 3.8 or higher
- CUDA 11.0+ (for GPU acceleration, optional but recommended)
- Sufficient storage for datasets (varies by data size)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/BMIRDS/PNN-MultiModal.git
cd PNN-MultiModal
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Data Preparation

1. Prepare your data in the following format:
   - **mIF Images**: TIFF or PNG format, organized by patient/region
   - **Spatial Transcriptomics**: H5AD format (Anndata) or CSV with spatial coordinates
   - **Clinical Metadata**: CSV with patient IDs and clinical features

2. Place data in the `data/` directory following the structure defined in `data_preparation.ipynb`

3. Run preprocessing notebooks to standardize and normalize data

### Quick Start

1. Start with `notebooks/data_exploration.ipynb` to understand your data
2. Run `notebooks/preprocessing.ipynb` to prepare datasets
3. Execute `notebooks/model_training.ipynb` to train models
4. Analyze results with `notebooks/evaluation.ipynb`

## Usage

### Training a Model

```python
from src.models import MultimodalDNN
from src.data import DataLoader

# Load and prepare data
train_loader = DataLoader.load_train_data('data/train')
val_loader = DataLoader.load_val_data('data/val')

# Initialize model
model = MultimodalDNN(
    img_channels=5,          # Number of protein markers
    transcriptomics_dim=2000, # Number of genes
    clinical_features=10      # Number of clinical features
)

# Train model
model.train(train_loader, val_loader, epochs=50, learning_rate=0.001)

# Evaluate
results = model.evaluate(test_loader)
```

### Making Predictions

```python
# Load trained model
model = MultimodalDNN.load('results/best_model.pt')

# Prepare patient data
patient_data = {
    'mif_image': img_array,
    'transcriptomics': expr_vector,
    'clinical': clinical_features
}

# Predict epilepsy risk
prediction = model.predict(patient_data)
print(f"Seizure Risk Score: {prediction['risk_score']:.3f}")
print(f"Feature Importance: {prediction['important_features']}")
```

## Data Format Specifications

### Multiplex Immunofluorescence Images
- Format: Multi-channel TIFF (one channel per protein marker)
- Resolution: 512×512 or higher
- Channels: 3-6 protein markers (e.g., GFAP, Iba1, CD3, NeuN, DAPI)
- Output: Normalized to [0, 1] range

### Spatial Transcriptomics
- Format: H5AD (AnnData) or CSV
- Content: Gene expression matrix with spatial coordinates
- Genes: Full transcriptome or pre-selected marker genes (500-5000)
- Output: Log-normalized expression values

### Clinical Metadata
- Format: CSV
- Fields: Patient ID, age, gender, tumor grade, tumor location, seizure status, etc.
- Output: Standardized features with appropriate scaling

## Model Architecture

The framework employs a multimodal neural network architecture:

1. **Image Encoder**: CNN-based encoder for spatial protein patterns
2. **Transcriptomics Encoder**: Graph neural network or transformer for gene expression
3. **Clinical Encoder**: Fully connected layers for tabular clinical data
4. **Fusion Layer**: Multi-head attention mechanism for cross-modal interactions
5. **Prediction Head**: Binary classification for seizure risk or regression for risk score

For detailed architecture descriptions, see `src/models/README.md`

## Results and Evaluation

The model is evaluated using:

- **Classification Metrics**: Accuracy, Precision, Recall, F1-Score, AUC-ROC
- **Cross-Validation**: Stratified 5-fold cross-validation
- **Feature Importance**: SHAP values and attention weights
- **Ablation Studies**: Analysis of contribution from each modality
- **Clinical Validation**: Performance on held-out test cohort

Results are saved in `results/` directory with visualizations and detailed reports.

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{pnn_multimodal_2026,
  title={PNN-MultiModal: Multimodal Deep Learning for Brain Tumor-Related Epilepsy Prediction},
  author={Liu, Wenjun and Sadanandappa, Madhumala and Palisoul, Scott and Zanazzi, George and Hong, Jennifer and Hassanpour, Saeed},
  year={2026},
  url={https://github.com/BMIRDS/PNN-MultiModal}
}
```

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Contributing

We welcome contributions from the research community! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request with a clear description of changes

For major changes, please open an issue first to discuss proposed modifications.

## Support and Contact

For questions, issues, or suggestions, please:

- Open an issue on [GitHub Issues](https://github.com/BMIRDS/PNN-MultiModal/issues)
- Contact the BMIRDS lab: [Visit BMIRDS](https://github.com/BMIRDS)
- Check existing documentation in the `docs/` directory

---

**Last Updated**: 2026  
**Status**: Active Development  
**Maintainers**: BMIRDS Team
