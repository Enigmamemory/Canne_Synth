import sys
from canne import *
import os
import pygame

mode = OperationMode(train=False,new_init=False,control=True)
synth = ANNeSynth(mode)






synth.load_weights_into_memory()
pygame.init()
pygame.mixer.init(channels=1)





tmp = np.zeros((1,9))
tmp[0,0] = 30#self.s1.value()
tmp[0,1] = 10#self.s2.value()
tmp[0,2] = 10#self.s3.value()
tmp[0,3] = 30#self.s4.value()
tmp[0,4] = 10#self.s5.value()
tmp[0,5] = 30#self.s6.value()
tmp[0,6] = 30#self.s7.value()
tmp[0,7] = 10#self.s8.value()
tmp /= 10.
tmp[0,8] = 2*10#self.s9.value()
#text, ok = QInputDialog.getText(self, 'Save File', 'Enter filename:')
#text = 
#ok = True
#if ok:
print('thishsouldprint')
filename_= 'somesound'
synth.execute(tmp,filename_)