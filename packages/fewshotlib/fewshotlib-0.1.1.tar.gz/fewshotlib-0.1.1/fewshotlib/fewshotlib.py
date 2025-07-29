import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as T
from PIL import Image
import os

class FewShotClassifier:
    def __init__(self, model_path, transform=None, USE_GPU=True):
        if USE_GPU and torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at path: {model_path}")

        try:
            checkpoint = torch.load(model_path, map_location=self.device)
        except Exception as e:
            raise RuntimeError(f"Failed to load the model: {e}")

        if "backbone" not in checkpoint:
            raise KeyError("Missing 'backbone' in the checkpoint.")
        if "prototypes" not in checkpoint:
            raise KeyError("Missing 'prototypes' in the checkpoint.")

        self.backbone = checkpoint["backbone"]
        self.image_format = checkpoint.get("image_format", "RGB")
        self.encoder = get_encoder(self.backbone, self.image_format).to(self.device)

        self.prototypes = checkpoint["prototypes"].to(self.device)
        self.labels = checkpoint.get("labels", None)

        self.transform = transform
        if self.transform is None:
            if "transform" in checkpoint:
                try:
                    self.transform = checkpoint["transform"]
                except Exception as e:
                    raise RuntimeError(f"Failed to load transform from checkpoint: {e}")
            else:
                self.transform = get_default_transform(self.image_format)

    def _load_and_preprocess(self, img_path):
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Image file not found: {img_path}")

        try:
            image = Image.open(img_path).convert(self.image_format)
        except Exception as e:
            raise RuntimeError(f"Failed to load image: {img_path}. Error: {e}")

        try:
            img_tensor = self.transform(image)
        except Exception as e:
            raise RuntimeError(f"Transform failed for image {img_path}: {e}")

        # Handle grayscale if model expects 3 channels
        if img_tensor.ndim == 2:
            img_tensor = img_tensor.unsqueeze(0)
        elif img_tensor.ndim == 3 and img_tensor.shape[0] == 1 and self.image_format == "RGB":
            img_tensor = img_tensor.repeat(3, 1, 1)
        elif img_tensor.ndim == 3 and img_tensor.shape[0] == 3 and self.image_format == "L":
            img_tensor = img_tensor[0:1]

        return img_tensor

    def predict(self, img_paths):
        single_input = False
        if isinstance(img_paths, str):
            img_paths = [img_paths]
            single_input = True
        elif not isinstance(img_paths, list):
            raise ValueError("img_paths must be a string or a list of strings")

        try:
            imgs = [self._load_and_preprocess(p) for p in img_paths]
        except Exception as e:
            raise RuntimeError(f"Image preprocessing failed: {e}")

        batch = torch.stack(imgs).to(self.device)

        with torch.no_grad():
            try:
                features = self.encoder(batch)
            except Exception as e:
                raise RuntimeError(f"Encoder inference failed: {e}")

            if features.ndim == 4:
                features = torch.nn.functional.adaptive_avg_pool2d(features, (1, 1))
                features = features.view(features.size(0), -1)

            features = torch.nn.functional.normalize(features, dim=1)
            prototypes = torch.nn.functional.normalize(self.prototypes, dim=1)

            sim = torch.matmul(features, prototypes.T)
            preds = sim.argmax(dim=1).tolist()

        results = []
        for i, idx in enumerate(preds):
            label = self.labels[idx] if self.labels and idx < len(self.labels) else idx
            results.append({
                "file": img_paths[i],
                "index": idx,
                "label": label
            })

        return results[0] if single_input else results


def get_default_transform(image_format):
    if image_format == "L":
        return T.Compose([
            T.Resize((224, 224)),
            T.Grayscale(num_output_channels=1),
            T.ToTensor(),
        ])
    else:
        return T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
        ])


def get_encoder(backbone_name, image_format):
    if backbone_name == 'resnet18':
        model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        if image_format == "L":
            model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        model = nn.Sequential(*list(model.children())[:-1])

    elif backbone_name == 'resnet34':
        model = models.resnet34(weights=models.ResNet34_Weights.IMAGENET1K_V1)
        if image_format == "L":
            model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        model = nn.Sequential(*list(model.children())[:-1])

    elif backbone_name == 'resnet50':
        model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        if image_format == "L":
            model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        model = nn.Sequential(*list(model.children())[:-1])

    elif backbone_name == 'mobilenet_v2':
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
        if image_format == "L":
            model.features[0][0] = nn.Conv2d(1, 32, kernel_size=3, stride=2, padding=1, bias=False)
        model = model.features

    elif backbone_name == 'mobilenet_v3_small':
        model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
        if image_format == "L":
            model.features[0][0] = nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1, bias=False)
        model = model.features

    elif backbone_name == 'mobilenet_v3_large':
        model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.IMAGENET1K_V1)
        if image_format == "L":
            model.features[0][0] = nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1, bias=False)
        model = model.features

    elif backbone_name == 'efficientnet_b0':
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
        if image_format == "L":
            model.features[0][0] = nn.Conv2d(1, 32, kernel_size=3, stride=2, padding=1, bias=False)
        model = model.features

    elif backbone_name == 'efficientnet_b1':
        model = models.efficientnet_b1(weights=models.EfficientNet_B1_Weights.IMAGENET1K_V1)
        if image_format == "L":
            model.features[0][0] = nn.Conv2d(1, 32, kernel_size=3, stride=2, padding=1, bias=False)
        model = model.features

    elif backbone_name == 'densenet121':
        model = models.densenet121(weights=models.DenseNet121_Weights.IMAGENET1K_V1)
        if image_format == "L":
            model.features.conv0 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        model = nn.Sequential(*list(model.features.children()))

    elif backbone_name == 'densenet169':
        model = models.densenet169(weights=models.DenseNet169_Weights.IMAGENET1K_V1)
        if image_format == "L":
            model.features.conv0 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        model = nn.Sequential(*list(model.features.children()))

    else:
        raise ValueError(f"Backbone '{backbone_name}' not supported!")

    return model.eval()
