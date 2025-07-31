import torch
import math
def fftLoss(input,target,dim=-1,meanOut=True,norm="ortho",absGain=1,angleGain=1):
    inputFFT=torch.fft.fftn(input,dim=dim,norm=norm)
    targetFFT=torch.fft.fftn(target,dim=dim,norm=norm)
    absLoss=(inputFFT.abs()-targetFFT.abs()).abs()
    #absLoss[~torch.isfinite(absLoss)]=0
    angleLoss=(1-(inputFFT.angle()-targetFFT.angle()).cos())/2
    #angleLoss[~torch.isfinite(angleLoss)]=0
    loss=angleLoss*angleGain+absLoss*absGain
    if meanOut:
        return loss.mean()
    else:
        return loss
        
