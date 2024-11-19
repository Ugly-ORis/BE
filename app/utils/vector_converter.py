import base64
from io import BytesIO
from typing import List
import numpy as np
from PIL import Image
import torch
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1
from sklearn.decomposition import PCA

class VectorConverter:
    def __init__(self):
        """
        이미지를 벡터로 변환하는 유틸리티 클래스입니다.
        """
        self.model = InceptionResnetV1(pretrained='vggface2').eval()
        self.transform = transforms.Compose([
            transforms.Resize((160, 160)),  
            transforms.ToTensor(), 
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        dummy_data = np.random.rand(1000, 512)
        self.pca = PCA(n_components=min(128, 100))
        self.pca.fit(dummy_data)


    def img_to_vector(self, img: Image.Image, output_dim: int = 512) -> np.ndarray:
        """
        이미지를 특징 벡터로 변환하여 반환합니다.

        Parameters:
            img (Image.Image): 입력 이미지.
            output_dim (int): 출력 벡터의 차원 (기본값은 512, 128로도 가능).

        Returns:
            np.ndarray: 이미지의 특징 벡터.
        """
        img_tensor = self.transform(img).unsqueeze(0)

        with torch.no_grad():
            vector = self.model(img_tensor).cpu().numpy().flatten()

        if output_dim == 128:
            vector = self.pca.fit_transform(vector.reshape(1, -1)).flatten()

        return vector.astype(np.float32)
