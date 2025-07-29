import torch
import math

class FWLU1DT(torch.nn.Module):
    def __init__(self,in_channels,out_channels,kernel_size,stride=1,padding=0,output_padding=0,dilation=1,groups=1,padding_mode='zeros',bias=True,gain=1,**kwargs):
        super(FWLU1DT, self).__init__()
        self.ConvP=torch.nn.ConvTranspose1d(in_channels,out_channels,kernel_size,stride=stride,padding=padding,output_padding=output_padding,dilation=dilation,groups=groups,padding_mode=padding_mode,bias=False,**kwargs)
        self.ConvN=torch.nn.ConvTranspose1d(in_channels,out_channels,kernel_size,stride=stride,padding=padding,output_padding=output_padding,dilation=dilation,groups=groups,padding_mode=padding_mode,bias=False,**kwargs)
        
        if bias:
            self.bias=torch.nn.Parameter(torch.zeros((out_channels,1),**kwargs),requires_grad=True)
        else:
            self.bias=None
              
        with torch.no_grad():
            torch.nn.init.orthogonal_(self.ConvP.weight,gain=gain)
            torch.nn.init.orthogonal_(self.ConvN.weight,gain=gain)
        
    def forward(self,input):
        inputP=input.clamp(min=0)
        inputN=input.clamp(max=0)   
        output=self.ConvP(inputP)+self.ConvN(inputN)
            
        if self.bias is not None:
            output=output+self.bias
        
        return output
  
