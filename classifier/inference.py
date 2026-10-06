import torch
import numpy as np

from torchvision.transforms import v2

from classifier.model import get_model

class Inference:
    def _create_transforms(self,z_norm=True,resize_tpl=(224,224)):
        transforms = [
            v2.ToImage(),
            v2.Resize(resize_tpl),
            v2.ToDtype(torch.float32,scale=True),
        ]

        if z_norm:
            transforms.append(v2.Normalize(mean=[0.485, 0.456, 0.406],std=[0.229, 0.224, 0.225]))

        return v2.Compose(transforms)

    def __init__(self,model_name="squeezenet_1_1",npz_file_path="pyt_classes.npz",weights_file="./pyt_squeezenet_model.pth"):
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self._class_labels = np.load(npz_file_path)["arr_0"]
        print(f"Class labels: {self._class_labels}")

        self._model = get_model(model_name,weights_file=weights_file).to(self._device,memory_format=torch.channels_last)

        self._transforms = self._create_transforms()

    def predict_single(self,img,threshold:float=0.5)->tuple[str,float]:
        img_tensor = self._transforms(img).unsqueeze(dim=0).to(self._device,memory_format=torch.channels_last)

        self._model.eval()

        with torch.no_grad():
            preds = self._model(img_tensor)

            pred_probs = torch.nn.functional.softmax(preds,dim=1)

            pred_prob,pred_class_idx = torch.max(pred_probs,dim=1)
            pred_prob = pred_prob.item()
            pred_class_idx = pred_class_idx.item()

        print(pred_probs)
        pred_label = self._class_labels[pred_class_idx] if pred_prob >= threshold else "other"

        return pred_label,pred_prob

    def predict(self,imgs,threshold:float=0.5):
        img_tensors = torch.stack([self._transforms(img) for img in imgs]).to(self._device,memory_format=torch.channels_last)

        self._model.eval()

        predictions = list()
        with torch.no_grad():
            preds = self._model(img_tensors)

            pred_probs = torch.nn.functional.softmax(preds,dim=1)

            pred_probs,pred_class_idxs = torch.max(pred_probs,dim=1)

            predictions = [
                (self._class_labels[idx].item() if prob >= threshold else "other",prob.item()) for idx,prob in zip(pred_class_idxs,pred_probs)
            ]

        return predictions



if __name__ == "__main__":
    import glob
    import cv2

    inference_obj = Inference()

    sample_images = list()
    image_names = glob.glob("./images/*.jpg")

    for image_name in image_names:
        sample_images.append(cv2.imread(image_name))

    predictions = inference_obj.predict(sample_images)

    for img_name,(class_label,pred_prob) in zip(image_names,predictions):
        print(f"{img_name} ===> {class_label} with probability {pred_prob:.4f}")

    #sample_img = torch.randint(0,255,size=(10,3,300,300))


    #inference_obj.predict_single(sample_img)
    #inference_obj.predict(sample_img)
