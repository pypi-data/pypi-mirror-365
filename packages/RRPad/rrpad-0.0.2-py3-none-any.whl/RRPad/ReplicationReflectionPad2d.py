import math
import torch
import numpy as np
#padding为整数或(padding_left,padding_right,padding_top,padding_bottom)
class ReplicationReflectionPad2d(torch.nn.Module):
    def __init__(self,padding):
        super(ReplicationReflectionPad2d, self).__init__()
        if isinstance(padding,tuple):
            self.padding=padding
        else:
            self.padding=(padding,padding,padding,padding)


    def forward(self,input):
        nextPadding=self.padding
        output=input
        if(input.size(2)==0 or input.size(3)==0):
            output=torch.nn.functional.pad(output,self.padding)
            nextPadding=(0,0,0,0)
        if(input.size(2)==1):
            output=torch.nn.functional.pad(output,tuple(np.array(nextPadding)*[0,0,1,1]),'replicate')
            nextPadding=tuple(np.array(nextPadding)*[1,1,0,0])
        if(input.size(3)==1):
            output=torch.nn.functional.pad(output,tuple(np.array(nextPadding)*[1,1,0,0]),'replicate')
            nextPadding=tuple(np.array(nextPadding)*[0,0,1,1])
        while(nextPadding[0]!=0 or nextPadding[1]!=0 or nextPadding[2]!=0 or nextPadding[3]!=0):
            padding=tuple(np.minimum(np.abs(nextPadding),(output.size(3)-1,output.size(3)-1,output.size(2)-1,output.size(2)-1))*np.sign(nextPadding))
            nextPadding=tuple(np.array(nextPadding)-padding)
            output=torch.nn.functional.pad(output,padding,'reflect')
        return output

