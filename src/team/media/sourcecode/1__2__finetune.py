import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from torch.optim import lr_scheduler
import numpy as np
from torchvision import models, transforms
import os
import copy
import time
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as nf
import pandas as pd
from skimage import io, transform

## Load the data
class LandmarksDataset(Dataset):
    def __init__(self, csv_file, root_dir, transform=None):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.landmarks_frame = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.landmarks_frame)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir,
                                self.landmarks_frame.iloc[idx, 1])+'.jpg'
        label = self.landmarks_frame.iloc[idx, 3]
        image = io.imread(img_name)

        # sample = {'image': image, 'label':torch.LongTensor(label)}
        sample = {'image': image, 'label': label}
        if self.transform:
            sample = self.transform(sample)

        return sample

class TestLandmarksDataset(Dataset):
    def __init__(self, csv_file, root_dir, transform=None):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.landmarks_frame = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.landmarks_frame)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir,
                                self.landmarks_frame.iloc[idx, 1])+'.jpg'
        image = io.imread(img_name)
        sample = {'image': image}
        if self.transform:
            sample = self.transform(sample)

        return sample


class Rescale(object):
    """Rescale the image in a sample to a given size.

    Args:
        output_size (tuple or int): Desired output size. If tuple, output is
            matched to output_size. If int, smaller of image edges is matched
            to output_size keeping aspect ratio the same.
    """

    def __init__(self, output_size):
        assert isinstance(output_size, (int, tuple))
        self.output_size = output_size

    def __call__(self, sample):
        image = sample['image']

        h, w = image.shape[:2]
        if isinstance(self.output_size, int):
            if h > w:
                new_h, new_w = self.output_size * h / w, self.output_size
            else:
                new_h, new_w = self.output_size, self.output_size * w / h
        else:
            new_h, new_w = self.output_size

        new_h, new_w = int(new_h), int(new_w)

        img = transform.resize(image, (new_h, new_w))
        sample['image']=img

        return sample


class RandomCrop(object):
    """Crop randomly the image in a sample.

    Args:
        output_size (tuple or int): Desired output size. If int, square crop
            is made.
    """

    def __init__(self, output_size):
        assert isinstance(output_size, (int, tuple))
        if isinstance(output_size, int):
            self.output_size = (output_size, output_size)
        else:
            assert len(output_size) == 2
            self.output_size = output_size

    def __call__(self, sample):
        image = sample['image']

        h, w = image.shape[:2]
        new_h, new_w = self.output_size

        top = np.random.randint(0, h - new_h)
        left = np.random.randint(0, w - new_w)

        image = image[top: top + new_h,
                      left: left + new_w]
        sample['image']=image
        return sample


class ToTensor(object):
    """Convert ndarrays in sample to Tensors."""

    def __call__(self, sample):
        image= sample['image']

        # swap color axis because
        # numpy image: H x W x C
        # torch image: C X H X W
        image = image.transpose((2, 0, 1))
        sample['image']=torch.from_numpy(image)
        return sample

data_dir = 'hw7data/images/'
# dataset = LandmarksDataset(csv_file='hw7data/train_sample.csv',
dataset = LandmarksDataset(csv_file='hw7data/train.csv',
                            root_dir='hw7data/images/',
                           transform=transforms.Compose([Rescale(256),RandomCrop(224),ToTensor()]))

dataloader = torch.utils.data.DataLoader(dataset, batch_size=64, shuffle=True, num_workers=4)
dataset_sizes = len(dataset)
class_names = [0,1,2,3,4,5,6,7,8,9]

device = torch.device("cpu")


## Fine-tune (train) your model for the target task.

def train_model(model, criterion, optimizer, scheduler, num_epochs=2):
    since = time.time()

    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0
    model = model.double()

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)

        scheduler.step()
        model.train()  # Set model to training mode

        running_loss = 0.0
        running_corrects = 0


        # Iterate over data.
        for idx, sample in enumerate(dataloader):

            # print('type of idx',type(idx))
            # print('type of sample', type(sample))
            # print('type of sample[image]', type(sample['image']))
            # print('type of sample[label]', type(sample['label']))
            print("running idx=",idx,', with label=',sample['label'])
            inputs = sample['image'].to(device)
            # labels = sample['label'].to(device)

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward
            # track history if only in train
            with torch.set_grad_enabled(True):
                outputs = model(inputs)
                outputs=nf.log_softmax(outputs,dim=1)
                # _, preds = torch.max(outputs, 1)
                # preds =nn.Softmax(preds,dim=1)
                # loss = criterion(outputs, labels)
                loss = criterion(outputs, Variable(sample['label']))
                # loss = criterion(outputs, torch.max(labels, 1)[1])

                # backward + optimize
                loss.backward()
                optimizer.step()

                outputs = model(inputs)
                outputs = nf.log_softmax(outputs, dim=1)
                print('outputs.dim:', np.argmax(outputs.detach().numpy().astype(np.long), axis=1).ravel())

            # statistics
            running_loss += loss.item() * len(sample)
            # for i in range(len(preds)):
            #     if preds[i]==sample['label'][0]:
            #         running_corrects+=1
            running_corrects += (np.argmax(outputs.detach().numpy().astype(np.long),axis=1).ravel() == sample['label'].detach().numpy().astype(np.long)).ravel().sum()

        print('correct:',running_corrects,', datasize:',dataset_sizes)
        epoch_loss = running_loss / dataset_sizes
        epoch_acc = running_corrects / dataset_sizes

        print('Loss: {:.4f} Acc: {:.4f}'.format(epoch_loss, epoch_acc))
        best_acc = epoch_acc
        best_model_wts = copy.deepcopy(model.state_dict())



        print()

    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))

    # load best model weights
    model.load_state_dict(best_model_wts)
    return model

model_ft = models.resnet18(pretrained=True)
num_ftrs = model_ft.fc.in_features
model_ft.fc = nn.Linear(num_ftrs, 10)

model_ft = model_ft.to(device)

criterion = nn.CrossEntropyLoss()

# Observe that all parameters are being optimized
optimizer_ft = optim.SGD(model_ft.parameters(), lr=0.001, momentum=0.9)
# Decay LR by a factor of 0.1 every 7 epochs
exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=7, gamma=0.1)
model_ft = train_model(model_ft, criterion, optimizer_ft, exp_lr_scheduler,
                       num_epochs=2)

## Use the model to predict the classes of the test images.
test_dataset = TestLandmarksDataset(csv_file='hw7data/test.csv',
                                root_dir='hw7data/images/',
                                transform=transforms.Compose([Rescale(256),RandomCrop(224),ToTensor()]))

test_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=1, shuffle=False, num_workers=4)
submission = open('submission.txt','w')
submission.write('landmark_id\n')
for idx, sample in enumerate(test_dataloader):
    inputs = sample['image'].to(device)
    outputs = model_ft(inputs)
    outputs = nf.log_softmax(outputs, dim=1)
    submission.write(str(np.argmax(outputs.detach().numpy().astype(np.long), axis=1).ravel()[0]))
    submission.write('\n')


submission.close()
