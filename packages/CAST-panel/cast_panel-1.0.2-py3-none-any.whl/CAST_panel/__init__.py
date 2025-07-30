import numpy as np
from scipy.stats import norm
import pandas as pd

from collections import defaultdict

#########################################################################################


def svds(M, r):
    # Computes the rth order SVD of matrix M
    # M: numpy array of size (n,m)
    # r: int representing the order of SVD

    # returns
    # u: numpy array of size (n, r), denoting left singular components
    # s: numpy array of size r, denoting the singular values
    # vh: numpy array of size (r, m), the right singular components

    u, s, vh = np.linalg.svd(M)
    return u[:,0:r], s[0:r], vh[0:r,:]



def spectral_4_block(M, N, T, N1, T1, r):
    # Computes an estimate for the missing bottom-right block under four-block design
    # M: numpy array of size (N,T) 
    # M = [M_a, M_b; M_c, ?] 
    # (N1,T1): the size of numpy array M_a
    # r: the underlying rank
    
    # returns
    # Md_hat: numpy array of size (N-N1,T-T1), an estimate of the ? block in M
    
    # Extract the left block of size (N,T1) and the upper block of size (N1,T)
    M_left = M[:,0:T1]
    M_upper = M[0:N1,:]
    # Estimate an orthonormal basis U_left for the column subspace of the full matrix
    U_left, Sigma_left, V_left_t = svds(M_left,r)
    # Denoise the upper block M_left and extract an denoised estimate Mb_hat for M_b
    U_upper, Sigma_upper, V_upper_t = svds(M_upper,r)
    Mb_hat = np.matmul(np.matmul(U_upper,np.diag(Sigma_upper)),V_upper_t[:,T1:T])
    # Use linear regression to compute an estimate for the missing block
    U1 = U_left[0:N1,:]
    U2 = U_left[N1:N,:]
    Md_hat = np.matmul(np.matmul(np.matmul(U2,np.linalg.inv(np.matmul(U1.T,U1))),U1.T),Mb_hat)
    return Md_hat



#######################################################################################3


class causal_panel:
    # Class that runs the causal panel method
    # Instruction: 
    # Step 1: initialize the class with obj = causal_panel(M,A)
    # Step 2: call obj.check_svd() to visualize the spectrum
    # Step 3: choose a rank r, and use obj.set_rank(r) to set the rank
    # Step 4: call obj.run_algorithm(alpha) to construct entrywise (1-alpha)-confidence intervals for the missing entries


    def __init__(self, M, A):
        # initializes the class
        # inputs:
        # M : numpy array of size (N,T) denoting the measured outcomes under control
        # A : numpy (binary) array of size (N,T) denoting the unit time pairs that 
        #        are observed (1) or unobserved (0) in the matrix M

        # stores relevant information
        self.M = M
        self.A = A
        self.N, self.T = np.shape(M) # saves the number of units (N) and length (T)

        # sorts the rows of M and A from latest adoption of treatment to earliest
        treatment_time = np.sum(self.A, axis=1) # how long a unit is under treatment
        self.index = np.argsort(-treatment_time) 
        self.A_sorted = self.A[self.index,:] # sort the rows of A
        self.M_sorted = self.M[self.index,:]

        self.index_inv = np.argsort(self.index) 
        # if we want to get back to the original order of A, just use self.A_sorted[index_inv,:], self.M_sorted[index_inv,:]

        # computes all possible values of length of treatment and sorts
        T_all = np.sort(np.unique(treatment_time))
        self.T_all = T_all.astype(np.int32)
        self.k = T_all.shape[0] # number of different groups

        # constructs N_all, 1D array where N_all[i] is number of units with treatment
        # length up to the i^th longest treatment period
        N_all = np.zeros(self.k)
        for i in range(self.k):
            N_all[i] = np.sum(treatment_time==T_all[self.k-1-i]) + N_all[i-1]
        self.N_all = N_all.astype(np.int32)
        


    def check_svd(self,threshold = 20.0):
        # computes and visualizes the SVD of the "most representative" observed submatrix of M
        # threshold: displaying the singular values that is larger than the max sinular value / threshold
        
        # find the best block
        criteria = np.sqrt(1.0 / np.flip(self.N_all) + 1.0 / self.T_all)
        index = np.argmin(criteria)
        
        # Extract the best block out and compute its spectrum
        N1_hat = self.N_all[self.k-1-index]
        T1_hat = self.T_all[index]
        M_hat = self.M_sorted[0:N1_hat,0:T1_hat]
        u, s, vh = np.linalg.svd(M_hat)
        
        # Visualizing the top singular values
        max_len = np.sum(s > s[0] / threshold)
        if max_len < s.shape[0]:
            max_len += 1
        print('sub-block of dimension ', [N1_hat,T1_hat])
        print('top singular values:\n', s[0:max_len])
        print('ratios:\n',s[0:(max_len-1)]/s[1:max_len])
        plt.plot(range(1,max_len+1),s[0:max_len],'.-')
        plt.show()
    


    def set_rank(self, r):
        # setting the underlying rank r
        self.r = r
        


    def estimate_missing(self):
        # Compute an estimate for each of the missing sub-matrices
        # output:
        # M_est: (self.N, self.T) array, a matrix with only estimated counterfactual entries; observed entries are 0
        M_est = np.zeros([self.N,self.T])
        
        for i in range(self.k):
            for j in range(self.k-i,self.k):
                k1 = self.k - j - 1
                k2 = self.k - i - 1
                N1_ij = self.N_all[k1] # parameter N1 of the constructed "four-block" matrix
                T1_ij = self.T_all[k2] # parameter T1 of the constructed "four-block" matrix
                N_ij = self.N_all[i] # parameter N of the constructed "four-block" matrix
                T_ij = self.T_all[j] # parameter T of the constructed "four-block" matrix
                M_ij = self.M_sorted[0:N_ij,0:T_ij] # the constructed "four-block" matrix

                M_d_ij = spectral_4_block(M_ij,N_ij,T_ij,N1_ij,T1_ij,self.r) # call function spectral_4_block to estimate the missing block
                
                M_est[self.N_all[i-1]:self.N_all[i],self.T_all[j-1]:self.T_all[j]] \
                    = M_d_ij[(self.N_all[i-1]-N1_ij):(self.N_all[i]-N1_ij),(self.T_all[j-1]-T1_ij):(self.T_all[j]-T1_ij)] # store the estimate
        
        self.M_est_sorted = M_est # This is a matrix with only estimated counterfactual entries; observed entries are 0
        self.M_impute_sorted = M_est + self.M_sorted * self.A_sorted # Impute the missing entries of the observed matrix with the estimation
        return M_est[self.index_inv,:]


    def estimate_parameters(self,iteration=1):
        # Compute an estimate for the full matrix (make sure that self.estimate_missing() is executed)
        u, s, vh = svds(self.M_impute_sorted,self.r)
        M_est_full = np.matmul(np.matmul(u,np.diag(s)),vh)
        E_est = (self.M_sorted - M_est_full) * self.A
        self.E_hat = E_est # an estimate for the noise matrix
        self.U_hat = u # an estimate for the left singular subspace
        self.V_hat = vh.T # an estimate for the right singular subspace
        


    def construct_CI(self, alpha=0.05):
        # Compute entrywise confidence intervals (make sure that self.estimate_parameters() is executed)
        # alpha: confidence levels for each entrywise confidence intervals
        std_est = np.zeros([self.N,self.T])

        for i in range(self.k):
            for j in range(self.k-i,self.k):
                k1 = self.k - j - 1
                k2 = self.k - i - 1
                N1_ij = self.N_all[k1] # parameter N1 of the constructed "four-block" matrix
                T1_ij = self.T_all[k2] # parameter T1 of the constructed "four-block" matrix
                N_ij = self.N_all[i] # parameter N of the constructed "four-block" matrix
                T_ij = self.T_all[j] # parameter T of the constructed "four-block" matrix

                # Estimation of model parameters for the constructed "four-block" matrix
                U = self.U_hat[0:N_ij,:] 
                V = self.V_hat[0:T_ij,:] 
                U1 = self.U_hat[0:N1_ij,:]
                V1 = self.V_hat[0:T1_ij,:]
                U2 = self.U_hat[N1_ij:N_ij,:]
                V2 = self.V_hat[T1_ij:T_ij,:]
                temp_U = np.square(np.matmul(np.matmul(U2,np.linalg.inv(np.matmul(U1.T,U1))),U1.T)) # (N_ij - N1_ij) by N1_ij
                temp_V = np.square(np.matmul(np.matmul(V2,np.linalg.inv(np.matmul(V1.T,V1))),V1.T)) # (T_ij - T1_ij) by T1_ij
                
                # Estimate the entrywise variance of the estimate
                var_est_ij = np.matmul(temp_U,np.square(self.E_hat[0:N1_ij,T1_ij:T_ij])) \
                    + np.matmul(np.square(self.E_hat[N1_ij:N_ij,0:T1_ij]),temp_V.T) # (N_ij - N1_ij) by (T_ij - T1_ij)
                std_est_ij = np.sqrt(var_est_ij) # compute the standard deviation
                std_est[self.N_all[i-1]:self.N_all[i],self.T_all[j-1]:self.T_all[j]] \
                    = std_est_ij[(self.N_all[i-1]-N1_ij):(self.N_all[i]-N1_ij),(self.T_all[j-1]-T1_ij):(self.T_all[j]-T1_ij)] # store the std

        self.std_est_sorted = std_est # entrywise standard deviation
        self.CI_upper_sorted = self.M_est_sorted + std_est * norm.ppf(1-alpha/2) # upper bounds for the entrywise confidence intervals
        self.CI_lower_sorted = self.M_est_sorted - std_est * norm.ppf(1-alpha/2) # lower bounds for the entrywise confidence intervals
    


    def run_algorithm(self, alpha=0.05):
        # run the algorithm
        self.estimate_missing()
        self.estimate_parameters()
        self.construct_CI(alpha)
        # Setting the final outputs (by reverting to the original order).
        self.M_est = self.M_est_sorted[self.index_inv,:]
        self.M_impute = self.M_impute_sorted[self.index_inv,:]
        self.CI_upper = self.CI_upper_sorted[self.index_inv,:]
        self.CI_lower = self.CI_lower_sorted[self.index_inv,:]
        self.std_est = self.std_est_sorted[self.index_inv,:]



    def ATE_CI(self, weight):
        # Compute ATE and SE for ATE in each year (make sure that self.run_algorithm() is executed)
        # self.ATE records the center or estimate of ATE for each column
        # self.std_ATE records the standard error fo the ATe estimate
        
        self.weight = weight
        self.weight_sorted = self.weight[self.index,:] 
        ATE = np.sum(self.weight_sorted * (self.M_sorted - self.M_impute_sorted), axis=0)
        
        record = np.zeros([self.T,self.N,self.T]) # recording all coefficients associated with entrywise estimate
        std_ATE = np.zeros([self.T])
        
        for i in range(self.k):
            for j in range(self.k-i,self.k):
                k1 = self.k - j - 1
                k2 = self.k - i - 1
                N1_ij = self.N_all[k1] # parameter N1 of the constructed "four-block" matrix
                T1_ij = self.T_all[k2] # parameter T1 of the constructed "four-block" matrix
                N_ij = self.N_all[i] # parameter N of the constructed "four-block" matrix
                T_ij = self.T_all[j] # parameter T of the constructed "four-block" matrix

                # Estimation of model parameters for the constructed "four-block" matrix
                U = self.U_hat[0:N_ij,:] 
                V = self.V_hat[0:T_ij,:]
                U1 = self.U_hat[0:N1_ij,:]
                V1 = self.V_hat[0:T1_ij,:]
                U2 = self.U_hat[N1_ij:N_ij,:]
                V2 = self.V_hat[T1_ij:T_ij,:]
                temp_U = np.matmul(np.matmul(U2,np.linalg.inv(np.matmul(U1.T,U1))),U1.T) # (N_ij - N1_ij) by N1_ij
                temp_V = np.matmul(np.matmul(V2,np.linalg.inv(np.matmul(V1.T,V1))),V1.T) # (T_ij - T1_ij) by T1_ij

                # Record params
                for jj in range(self.T_all[j-1],self.T_all[j]):
                    for ii in range(self.N_all[i-1],self.N_all[i]):
                        record[jj,ii,0:T1_ij] = temp_V[jj-T1_ij,:] * self.weight_sorted[ii,jj]
                        record[jj,0:N1_ij,jj] += self.weight_sorted[ii,jj] * temp_U[ii-N1_ij,:]
        
        for jj in range(self.T):
            coef = record[jj,:,:]
            var_jj = np.sum(np.square(coef) * np.square(self.E_hat))
            std_jj = np.sqrt(var_jj)
            std_ATE[jj] = std_jj
        
        self.std_ATE = std_ATE # standard deviations
        # self.CI_ATE_upper = self.ATE + std_ATE * norm.ppf(1-alpha/2) # upper bounds for the confidence intervals
        # self.CI_ATE_lower = self.ATE - std_ATE * norm.ppf(1-alpha/2) # lower bounds for the confidence intervals

        return ATE, std_ATE



#######################################################################################


class method:


    def __init__(self, observations, treat_index, rank, alpha = 0.95):
        # initializes the method
        # observations: numpy array of dimensions (N,T) where N is number of units
        #               and T is number of time_periods 
        # treat_index: numpy array of size N indicating the index for which treatment
        #               begins in observations
        # rank: int denoting what rank to use, default = 0 which indicates an automated
        #       procedure (automated to be implemented later)
        # alpha: coverage of the confidence intervals

        # exceptions to throw
        if len(treat_index) != observations.shape[0]:
            raise Exception("Number of units in treat_index does not match the \
                                number of units in observations")

        if not self._check_valid(rank):
            raise Exception("Rank is not a non-negative integer.")

        self.observations = observations
        self.num_units = self.observations.shape[0]

        self._controls = method._control_mask(observations, treat_index)

        self.treat = 1 - self._controls


        # initializes the method
        self.method = causal_panel(self.observations, self._controls)

        # sets the rank
        if rank == 0:
            # probably not implemented yet
            self._rank_selection(rank_select)
        else:
            self.method.set_rank(rank)

        self.method.run_algorithm(alpha)



    def set_rank(self, rank):
        # resets the rank and reruns the method
        # rank: int, indicating the rank to be run

        self.method.set_rank(rank)
        self.method.run_algorithm()



    def get_imputed_estimates(self):
        # returns two numpy arrays of dimension (N, T)
        # method.M_est: the estimated values of the counterfactual controls
        #                   and the observed controls are 0
        # self._controls: the matrix indicating which entires are estimated
        return self.method.M_est, self._controls



    def get_treatment_effects(self):
        # returns two numpy arrays of dimension (N, T) consisting of the
        # estimated individual treatment effect and the matrix indicating
        # which ones are the estimated effects 
        return self.observations - self.method.M_impute, self._controls 



    def get_significant_effects(self, alpha = 0.05):
        # returns a dataframe consisting of, for each time index, the number
        # of units with positive, negative, null, and under treatment
        # for that given time index

        num_treated = np.sum(self.treat, axis = 0)
        first_treat_index = np.sum(num_treated == 0)

        treat_effects, _ = self.get_treatment_effects()
        std_est = self.get_std_errors()

        positive_effects = np.multiply(self.treat, treat_effects > norm.ppf(1-alpha/2) * std_est)
        positive_effects = np.sum(positive_effects, axis = 0)

        negative_effects = np.multiply(self.treat, treat_effects < - norm.ppf(1-alpha/2) * std_est)
        negative_effects = np.sum(negative_effects, axis = 0)

        null_effects = num_treated - positive_effects - negative_effects

        data = {}
        data["Positive effects"] = positive_effects
        data["Negative effects"] = negative_effects
        data["Null effects"] = null_effects
        data["Number treatment"] = num_treated

        df = pd.DataFrame(data)
        df = df.iloc[first_treat_index:, :].reset_index(drop = True)

        return df



    def get_std_errors(self):
        # returns a dataframe consisting of, for each time index, the
        # standard error for the ITE estimate

        return self.method.std_est


    def get_average_effect(self, weights = None, num_treated_renorm = True):
        # returns the weighted average effect (on treated) and standard error for it for each time index
        # weights: numpy array of size N indicating the weight to use for unit i
        #           renormalized by total weight amongst the treated
        #           If weights is None, we use the default average
        # num_treated_renorm: boolean indicated if we want to rescale by 1/T_i, where T_i
        #           denotes the number of treated units in time period i

        if weights is None:
            weights = np.ones(self.num_units)
            weights = self.treat * weights[:, np.newaxis]

        num_treated = np.sum(self.treat, axis = 0)
        first_treat_index = np.sum(num_treated == 0)

        num_treated[:first_treat_index] = 1.

        if num_treated_renorm:
            weights = weights.astype(np.float64) / num_treated

        WTE, WTE_CI = self.method.ATE_CI(weights)

        return WTE[first_treat_index:], WTE_CI[first_treat_index:]


    @staticmethod
    def _check_valid(value):
        # returns true if value is a non-negative int
        return value >= 0 and (value == int(value))

    @staticmethod
    def _control_mask(observations, treat_index):
        # based on the treatment periods, constructs the mask indicating which 
        # in self.observations are under control

        controls = np.zeros(observations.shape)

        for i in range(observations.shape[0]):
            treat_begin = treat_index[i]

            if method._check_valid(treat_begin):
                controls[i, :treat_begin] = 1
            else:
                raise Exception("Invalid treatment index")

        return controls


#######################################################################################




def rank_selection(observations, treat_index):
    # recommends the rank based off spectral structure
    # rank_select: string denoting the method, options are (tentatively)
    #               Scree (look at the singular values directly), 
    #               ScreeNOT (Donoho's method)
    #               CNG (permutation test based method)

    controls = method._control_mask(observations, treat_index)
    mat_denoise = _get_matrix_denoise(observations, controls)

    sing_values = np.linalg.svd(mat_denoise)[1]


    # Broken-stick
    avg_sings = sing_values / np.sum(sing_values)
    harm = 0.

    j = len(avg_sings) - 1

    while j > 0:
        sing = avg_sings[j]
        harm += 1. / j

        if sing > j:
            break

        j -= 1

    broken_stick = j + 1
    
    values = {}
    values["singular_values"] = sing_values
    values["broken_stick"] = broken_stick

    return values



def _get_matrix_denoise(observations, controls):
    # gets the optimal submatrix to denoise based off of
    # i.e. the one with the largest
    treatment_time = np.sum(1 - controls, axis=1) # how long a unit is under treatment
    reverse_order = np.argsort(-treatment_time) 

    obs_block = observations[reverse_order, :]

    # chooses the optimal index
    treatlength_counts = defaultdict(int)

    for i in range(len(treatment_time)):
        treatlength_counts[treatment_time[i]] += 1

    keys = list(treatlength_counts.keys())
    keys.sort(reverse = True)

    run_N = 0
    max_value = np.inf


    for i in range(len(keys)):
        T = keys[i]
        run_N += treatlength_counts[T]

        if T == 0:
            break

        temp_value = 1 / np.sqrt(T) + 1 / np.sqrt(run_N)

        if temp_value < max_value:
            max_value = temp_value
            save_ind = (run_N, T)

    return obs_block[:int(save_ind[0]), :int(save_ind[1])]
