# Few-Shot Classifier Library

A lightweight Python library for image classification using few-shot learning. Given a small number of support images per class, this library classifies query images based on visual similarity using learnable embeddings.

## Features

- No training required — works directly with pretrained backbones
- Supports multiple popular models: ResNet, MobileNet, EfficientNet, DenseNet, and more
- Accepts individual images or batches for prediction
- **Automatically detects image type:** handles RGB and Grayscale images as required by the model
- Returns class indices or original labels (if provided)
- Easy integration with PyTorch pipelines

## Installation

Install directly from PyPI:

```

pip install fewshotlib

```

Or, if not yet published, install locally from source:

```

git clone https://github.com/RohitXJ/few-shot-lib.git
cd fewshotlib
pip install .

```

## How to Use

```

from fewshotlib import FewShotClassifier
from PIL import Image

# Load a model checkpoint (must be generated using our model creation utility)

model_path = 'model.pt'
classifier = FewShotClassifier(model_path)

# Predict from a single image file

result = classifier.predict('test_image.png')
print(result)

# Predict from a batch of image files

results = classifier.predict(['img1.png', 'img2.png'])
print(results)

# Predict and return the original class label (if available)

result = classifier.predict('test_image.png')
print(result['label'])  \# outputs the original label, if present

```

## Notes

- If your `model.pt` file contains labels from the prototype creation step, you will receive the corresponding original label for each prediction.
- The library automatically handles input images in RGB or Grayscale formats and applies the necessary preprocessing for the chosen backbone model.
- Supports file paths to images (recommended). For power users, you may load a PIL image and pass it directly, but file path input is default.

## Generate `model.pt`

To create a compatible `model.pt` file for this library, use our companion tool (coming soon):

```

https://github.com/RohitXJ/few-shot-web

```

This tool lets you select a few images per class and generates a `.pt` file storing class prototypes and labels.

## License

This project is licensed under a **Custom Research and Educational Use License**.

You are permitted to use, copy, modify, and distribute this software **only for research and educational purposes**. **Commercial use is strictly prohibited** without prior written permission from the author.

See the [LICENSE](./LICENSE) file for full terms.

For commercial inquiries, contact: [gomesrohit92@gmail.com](mailto:gomesrohit92@gmail.com)

