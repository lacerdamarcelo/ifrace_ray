import numpy as np
import pycuda.driver as cuda
from pycuda.compiler import SourceModule


class CEC17Function:
    def __init__(self, func_num, nx, MAX_INDIVIDUALS, module_path="cec17functions.cu"):
        self.func_num = func_num
        self.nx = nx
        # Read data from files
        self.OShift, self.M, self.y, self.z, self.SS = self.read_file(self.nx, self.func_num, MAX_INDIVIDUALS)
        # Load data into device
        self.OShift_dev = cuda.mem_alloc(self.OShift.nbytes)
        cuda.memcpy_htod(self.OShift_dev, self.OShift)
        self.M_dev = cuda.mem_alloc(self.M.nbytes)
        cuda.memcpy_htod(self.M_dev, self.M)
        self.y_dev = cuda.mem_alloc(self.y.nbytes)
        cuda.memcpy_htod(self.y_dev, self.y)
        self.z_dev = cuda.mem_alloc(self.z.nbytes)
        cuda.memcpy_htod(self.z_dev, self.z)
        self.SS_dev = None
        if self.SS is not None:
            self.SS_dev = cuda.mem_alloc(self.SS.nbytes)
            cuda.memcpy_htod(self.SS_dev, self.SS)
        else:
            # Allocating 4 bytes to avoid having a None pointer
            self.SS_dev = cuda.mem_alloc(4)
        self.func_num = np.int32(self.func_num)
        self.func_num_dev = cuda.mem_alloc(self.func_num.nbytes)
        cuda.memcpy_htod(self.func_num_dev, self.func_num)
        self.max_value = 100
        self.min_value = -100
        # Load functions cuda source
        with open(module_path, 'r') as f:
            self.cuda_module = f.read()        
        
    def read_file(self, nx, func_num, MAX_INDIVIDUALS):
        ini_flag = 0
        n_flag=-1
        func_flag=-1
        cf_num = 10

        if ini_flag==1:
            if (n_flag!=nx) or (func_flag!=func_num):
                ini_flag=0
        if ini_flag==0:
            y = np.zeros(nx * MAX_INDIVIDUALS)
            z = np.zeros(nx * MAX_INDIVIDUALS)
            if (nx==2 or nx==10 or nx==20 or nx==30 or nx==50 or nx==100) == False:
                print("Error: Test functions are only defined for D=2,10,20,30,50,100.")
            if nx==2 and ((func_num>=17 and func_num<=22) or (func_num>=29 and func_num<=30)):
                print("Error: hf07,hf08,hf09,hf10,cf01,cf02,cf09&cf10 are NOT defined for D=2.")
            # Load Matrix M
            with open("/home/marcelo/Documents/Doc_Cin/ecrl/algorithm/input_data/M_" + str(func_num) + "_D" + str(nx) + ".txt",'r') as f:
                lines = f.readlines()
                M = []
                for line in lines:
                    spt_lines = line.split(' ')
                    spt_lines[-1] = spt_lines[-1].split('\n')[0]
                    for value in spt_lines:
                        if value != '':
                            M.append(value)
                M = np.array(M).astype(np.float64)

            # Load shift_data
            with open("/home/marcelo/Documents/Doc_Cin/ecrl/algorithm/input_data/shift_data_" + str(func_num) + ".txt",'r') as f:
                lines = f.readlines()
                OShift = []
                for line in lines:
                    spt_lines = line.split(' ')
                    spt_lines[-1] = spt_lines[-1].split('\n')[0]
                    for value in spt_lines:
                        if value != '':
                            OShift.append(value)
                OShift = np.array(OShift).astype(np.float64)

            # Load Shuffle_data
            SS = None
            if (func_num>=11 and func_num<=20) or (func_num==29 or func_num==30):
                with open("/home/marcelo/Documents/Doc_Cin/ecrl/algorithm/input_data/shuffle_data_" + str(func_num) + "_D" + str(nx) + ".txt",'r') as f:
                    lines = f.readlines()
                    SS = []
                    for line in lines:
                        spt_lines = line.split('\t')
                        spt_lines[-1] = spt_lines[-1].split('\n')[0]
                        SS += spt_lines
                    SS = np.array(SS).astype(np.int32)

            n_flag=nx
            func_flag=func_num
            ini_flag=1
        return OShift, M, y, z, SS