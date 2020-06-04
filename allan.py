# function [T,sigma] = allan(omega,fs,pts)
# [N,M] = size(omega);             % figure out how big the output data set is
# n = 2.^(0:floor(log2(N/2)))';    % determine largest bin size
# maxN = n(end);
# endLogInc = log10(maxN);
# m = unique(ceil(logspace(0,endLogInc,pts)))';    % create log spaced vector average factor
# t0 = 1/fs;                                       % t0 = sample interval
# T = m*t0;                                        % T = length of time for each cluster
# theta = cumsum(omega)/fs;       % integration of samples over time to obtain output angle ¦È
# sigma2 = zeros(length(T),M);    % array of dimensions (cluster periods) X (#variables)
# for i=1:length(m)               % loop over the various cluster sizes
#     for k=1:N-2*m(i)            % implements the summation in the AV equation
#         sigma2(i,:) = sigma2(i,:) + (theta(k+2*m(i),:) - 2*theta(k+m(i),:) + theta(k,:)).^2;
#     end
# end
# sigma2 = sigma2./repmat((2*T.^2.*(N-2*m)),1,M);
# sigma = sqrt(sigma2);

# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import csv, math

class AllanAns():
    def __init__(self):
        self.data = np.loadtxt('./history/test.csv',skiprows=1, dtype=np.float ,delimiter=',')
        time1 = np.hstack((self.data[:, 0], np.array([0.0])))
        time2 = np.hstack((np.array([0.0]), self.data[:, 0]))
        self.time = (time1 - time2)[1:-1]
        self.data = np.delete(self.data, 0, axis=1)
        self.dt = np.average(self.time)

    def allan(self):
        NM = self.data.shape
        N = NM[0]
        M = NM[1]
        n = np.power(2, range(int(math.log2(N / 2))))
        maxN = n[-1]
        endLogInc = math.log10(maxN)
        # m = unique(ceil(logspace(0,endLogInc,pts)))';
        m = np.logspace(0, endLogInc, 100)
        t0 = self.dt
        fs = 1 / t0
        T = m * t0
        theta = np.cumsum(self.data, axis=0)/fs
        sigma2 = np.zeros((T.shape[0], M))
        for i in range(m.shape[0]):             # loop over the various cluster sizes
            for k in range(1, N - 2 * math.ceil(m[i])):
                sigma2[i,:] = sigma2[i,:] + \
                            np.power((theta[k+2*math.ceil(m[i]),:] - \
                            2*theta[k+math.ceil(m[i]),:] + \
                            theta[k,:]), 2)
        sigma2 = sigma2 / np.transpose(np.tile((2*np.power(T, 2.0)*(N-2*m)), (M, 1)))
        sigma = np.sqrt(sigma2)
        print("ok")
        plt.loglog(T, sigma[:, 0])
        plt.show()



a = AllanAns()
a.allan()