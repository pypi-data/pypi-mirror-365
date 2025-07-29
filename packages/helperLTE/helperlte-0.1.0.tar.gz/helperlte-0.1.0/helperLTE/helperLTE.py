import zipfile
import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from tqdm import tqdm
import time


def unzipFile(file_path, target_folder):
    """
    Verilmiş zip faylını təyin olunmuş qovluğa çıxarır.
    Əgər hədəf qovluq mövcud deyilsə, onu yaradır.

    Args:
        file_path (str): Çıxarılacaq zip faylının yolu.
        target_folder (str): Faylların çıxarılacağı qovluq.

    Returns:
        str: "Unzip Completed" mesajı.
    """
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(target_folder)
    return "Unzip Completed"


def calculateMeanStd(data_dir, batch_size=32, num_workers=2, image_size=(224, 224)):
    """
    Diskdə yerləşən şəkil datasetinin (ImageFolder strukturu) orta (mean) və standart sapma (std) dəyərlərini hesablayır.

    Args:
        data_dir (str): Datasetin yerləşdiyi qovluğun yolu. Qovluq alt-kataloqlar şəklində olmalıdır (hər biri bir class).
        batch_size (int): DataLoader üçün batch ölçüsü.
        num_workers (int): DataLoader üçün paralel işləyəcək işçi sayı.
        image_size (tuple): Şəkillərin ölçüsünü dəyişmək üçün istifadə olunan ölçü (hündürlük, en).

    Returns:
        mean (torch.Tensor): RGB kanalları üçün orta dəyərlər (shape: [3])
        std (torch.Tensor): RGB kanalları üçün standart sapmalar (shape: [3])
    """

    transform = transforms.Compose([
        transforms.Resize(image_size),
        transforms.ToTensor()
    ])

    dataset = datasets.ImageFolder(data_dir, transform=transform)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    n_channels = 3  
    mean = torch.zeros(n_channels)
    std = torch.zeros(n_channels)
    total_images = 0

    for images, _ in loader:
        batch_samples = images.size(0)  
        images = images.view(batch_samples, images.size(1), -1)
        mean += images.mean(2).sum(0)
        std += images.std(2).sum(0)
        total_images += batch_samples

    mean /= total_images
    std /= total_images

    print(f'Mean: {mean}')
    print(f'Std: {std}')


    return mean, std


def calculateMeanStdHF(hf_dataset):
    """
    Hugging Face dataset-indəki bütün şəkilləri RGB-yə çevirərək
    RGB kanallar üzrə orta (mean) və standart sapma (std) hesablayır.

    Args:
        hf_dataset: Hugging Face dataset obyektidir (məs: ds["train"])

    Returns:
        mean: np.ndarray, RGB üçün orta dəyərlər (shape: [3])
        std: np.ndarray, RGB üçün std dəyərlər (shape: [3])
    """
    to_tensor = transforms.ToTensor()
    n_images = len(hf_dataset)
    mean = np.zeros(3)
    std = np.zeros(3)
    rgb_count = 0

    for i in tqdm(range(n_images)):
        img = hf_dataset[i]['image']
        img = img.convert("RGB")  
        img = to_tensor(img)      
        mean += img.mean(dim=(1, 2)).numpy()
        std += img.std(dim=(1, 2)).numpy()
        rgb_count += 1

    mean /= rgb_count
    std /= rgb_count

    print(f'Mean: {mean}')
    print(f'Std: {std}')

    return mean, std


def transformWithAug(mean,std,img_size = 224):

    """
    Təlim və validasiya üçün şəkil çevirmələri (transformations) yaradır.
    Təlim çevirmələrinə data gücləndirmə (augmentation) daxildir.

    Args:
        mean (list or tuple): Normalizasiya üçün RGB kanallarının orta dəyərləri.
        std (list or tuple): Normalizasiya üçün RGB kanallarının standart sapma dəyərləri.
        img_size (int, optional): Şəkillərin ölçüləri (piksel). Defolt olaraq 224.

    Returns:
        tuple:
            train_transform (torchvision.transforms.Compose): Təlim üçün çevirmə ardıcıllığı.
            val_transform (torchvision.transforms.Compose): Validasiya üçün çevirmə ardıcıllığı.
    """

    IMG_SIZE = img_size

    train_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomRotation(10),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.8, 1.2), shear=10),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std)
    ])


    val_transform = transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std)
    ])

    return train_transform,val_transform


def datasetLoaderDevice(train_dir,val_dir,train_transform,val_transform,batch_size=32):
    
    """
    Verilmiş qovluqlardan şəkil məlumatlarını yükləyir, çevirmələri tətbiq edir
    və təlim (train) və validasiya (validation) üçün DataLoader obyektləri yaradır.
    Həmçinin istifadə olunan cihazı (CPU/GPU) müəyyən edir.

    Args:
        train_dir (str): Təlim şəkillərinin yerləşdiyi qovluğun yolu.
        val_dir (str): Validasiya şəkillərinin yerləşdiyi qovluğun yolu.
        train_transform (torchvision.transforms.Compose): Təlim üçün şəkil çevirmələri.
        val_transform (torchvision.transforms.Compose): Validasiya üçün şəkil çevirmələri.
        batch_size (int): DataLoader üçün istifadə olunacaq batch ölçüsü.

    Returns:
        tuple:
            train_loader (torch.utils.data.DataLoader): Təlim məlumatları üçün DataLoader.
            val_loader (torch.utils.data.DataLoader): Validasiya məlumatları üçün DataLoader.
    """
    train_dataset = datasets.ImageFolder(root=train_dir, transform=train_transform)
    val_dataset = datasets.ImageFolder(root=val_dir, transform=val_transform)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f'Your device: {device}')
    return train_loader,val_loader


def trainWithResnet18(train_loader,val_loader,num_classes,num_epochs=10):
 
    """
    ResNet18 modelini təlim edir. Model öncədən öyrədilmiş ağırlıqlarla yüklənir,
    son təbəqəsi verilən siniflərin sayına uyğunlaşdırılır.
    Təlim dövründə itki (loss) və dəqiqlik (accuracy) hesablanır və çap edilir.

    Args:
        num_classes (int): Təsnif ediləcək siniflərin sayı.
        num_epochs (int): Təlim dövrlərinin sayı.
        train_loader (torch.utils.data.DataLoader): Təlim məlumatları üçün DataLoader.
        val_loader (torch.utils.data.DataLoader): Validasiya məlumatları üçün DataLoader.

    Returns:
        torch.nn.Module: Təlim edilmiş model.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet18(pretrained=True)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0001)

    for epoch in range(num_epochs):
        start_time = time.time()
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total_train += labels.size(0)
            correct_train += (predicted == labels).sum().item()
        train_acc = 100 * correct_train / total_train
        print(f"Epoch [{epoch+1}/{num_epochs}] | Train Loss: {running_loss/len(train_loader):.4f}, Train Acc: {train_acc:.2f}%")

        # Doğrulama
        model.eval()
        val_loss = 0.0
        correct_val = 0
        total_val = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total_val += labels.size(0)
                correct_val += (predicted == labels).sum().item()
        val_acc = 100 * correct_val / total_val
        epoch_time = time.time() - start_time
        print(f"Val Loss: {val_loss/len(val_loader):.4f}, Val Acc: {val_acc:.2f}%, Time: {epoch_time:.2f} sec'")


    return model


def testEval(mean,std,test_dir,model,batch_size=32,IMG_SIZE=224):
    
    """
    Təlim keçmiş modeli test məlumatları üzərində qiymətləndirir.
    Test məlumatları üçün DataLoader yaradır, modelin itkisini (loss)
    və dəqiqliyini (accuracy) hesablayır və çap edir.

    Args:
        mean (list or tuple): Normalizasiya üçün RGB kanallarının orta dəyərləri.
        std (list or tuple): Normalizasiya üçün RGB kanallarının standart sapma dəyərləri.
        test_dir (str): Test şəkillərinin yerləşdiyi qovluğun yolu.
        model (torch.nn.Module): Qiymətləndiriləcək təlim keçmiş model.
        batch_size (int, optional): DataLoader üçün istifadə olunacaq batch ölçüsü. Defolt olaraq 32.
        IMG_SIZE (int, optional): Şəkillərin ölçüləri (piksel). Defolt olaraq 224.
    """
    test_transform = transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std)
    ])

    test_dataset = datasets.ImageFolder(root=test_dir, transform=test_transform)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0001) # Test mərhələsində optimizatorə ehtiyac yoxdur.
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model.eval()
    test_loss = 0.0
    correct_test = 0
    total_test = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            test_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total_test += labels.size(0)
            correct_test += (predicted == labels).sum().item()
    test_acc = 100 * correct_test / total_test
    print(f"Test Loss: {test_loss/len(test_loader):.4f}, Test Acc: {test_acc:.2f}%")
