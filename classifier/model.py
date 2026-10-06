import torch
from torchvision import models

def get_model(model_name="squeezenet_1_1",num_classes=5,weights_file = None)->torch.nn.Module:
    match model_name:
        case "squeezenet_1_1":
            return get_squeezenet_1_1(
                weights_file = weights_file,
                num_classes = num_classes
            )
        case _:
            raise Exception(f"No such model as {model_name}")

def get_squeezenet_1_1(weights_file:str|None = None,num_classes:int=5)->torch.nn.Module:
    model = models.squeezenet1_1(weights="DEFAULT")

    model.classifier[1] = torch.nn.Conv2d(512,num_classes,kernel_size=(1,1),stride=(1,1))

    if weights_file is not None:
        model.load_state_dict(torch.load(weights_file,weights_only=True))

    return model
