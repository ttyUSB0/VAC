#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 18:37:48 2018

@author: alex
"""
import numpy as np
import matplotlib.pyplot as plt


x = np.linspace(0,1,20)
y = x**2
f = plt.figure(0)
plt.clf()
plt.plot(x, y,'-*')
plt.xlabel('U, B')
plt.ylabel('I, A')
plt.grid()
f.show()
input('Нажимите любую клавишу для продолжения...')