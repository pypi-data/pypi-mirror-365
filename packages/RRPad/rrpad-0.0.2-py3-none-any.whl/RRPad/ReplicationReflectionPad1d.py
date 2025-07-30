import math
import torch
import numpy as np
#padding为整数或(padding_left,padding_right)
class ReplicationReflectionPad1d(torch.nn.Module):
    def __init__(self,padding):
        super(ReplicationReflectionPad1d, self).__init__()
        if isinstance(padding,tuple):
            self.padding=padding
        else:
            self.padding=(padding,padding)


    def forward(self,input):
        nextPadding=self.padding
        output=input
        if(input.size(2)==0):
            output=torch.nn.functional.pad(output,self.padding)
            nextPadding=(0,0)
        elif(input.size(2)==1):
            output=torch.nn.functional.pad(output,tuple(np.array(nextPadding)*[0,0,1,1]),'replicate')
            nextPadding=(0,0)
        while(nextPadding[0]!=0 or nextPadding[1]!=0):
            padding=tuple(np.minimum(np.abs(nextPadding),(output.size(2)-1,output.size(2)-1))*np.sign(nextPadding))
            nextPadding=tuple(np.array(nextPadding)-padding)
            output=torch.nn.functional.pad(output,padding,'reflect')
        return output

