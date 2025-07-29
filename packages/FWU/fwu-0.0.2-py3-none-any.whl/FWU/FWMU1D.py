import torch
import math

class FWMU1D(torch.nn.Module):
    def __init__(self,in_channels,out_channels,kernel_size,stride=1,padding=0,dilation=1,groups=1,padding_mode='zeros',bias=True,gain=1,**kwargs):
        super(FWMU1D, self).__init__()
        self.ConvP=torch.nn.Conv1d(in_channels,out_channels,kernel_size,stride=stride,padding=padding,dilation=dilation,groups=groups,padding_mode=padding_mode,bias=True,**kwargs)
        self.ConvN=torch.nn.Conv1d(in_channels,out_channels,kernel_size,stride=stride,padding=padding,dilation=dilation,groups=groups,padding_mode=padding_mode,bias=True,**kwargs)
        
        if bias:
            self.bias=torch.nn.Parameter(torch.zeros((out_channels,1),**kwargs),requires_grad=True)
        else:
            self.bias=None
              
        with torch.no_grad():
            torch.nn.init.orthogonal_(self.ConvP.weight,gain=gain)
            torch.nn.init.orthogonal_(self.ConvN.weight,gain=gain)
            torch.nn.init.normal_(self.ConvP.bias)
            self.ConvP.bias.data.sign_()
            torch.nn.init.normal_(self.ConvN.bias)
            self.ConvN.bias.data.sign_()
            
    def forward(self,input):
        inputP=input.clamp(min=0)
        inputN=input.clamp(max=0)   
        output=self.ConvP(inputP)*self.ConvN(inputN)-(self.ConvP.bias*self.ConvN.bias).unsqueeze(-1)
            
        if self.bias is not None:
            output=output+self.bias
        
        return output
  
