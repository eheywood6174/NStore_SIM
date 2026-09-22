"""Takes a full-length time-series of supply/demand data and a list of "down-sampling ratios";
generates one down-sampled version of the time-series for each down-sampling ratio.

Arguments:
orig_ts (ndarray): 1d array containing the original time-series data
DS_vec (ndarray): array containing the down-sampling ratios

Returns:
ds_array (list): a list containing the original time-series data and the down-sampled data arrays
"""
def make_DS_arrays(orig_ts, DS_vec):
    import numpy as np

    n_cell = len(DS_vec)
    n_hr = len(orig_ts)

    ds_array = [] #Initialise output list
    ds_array.append(orig_ts) #Install original array

    for i in range(n_cell):
        n_ds = int(np.round(DS_vec[i])) #How many orig samples per down-sample?
        m_ds =  int(np.ceil(n_hr/n_ds)) #How many down-samples in total?
        irange = np.arange(0, n_ds, dtype=int) #Identify the first set of data to down-sample
        ds_ts = np.zeros(m_ds) #Initialise array for down-sampled data
        for j in range(m_ds-1): #Populate the first (m_ds - 1) entries
            ds_ts[j] = sum([orig_ts[k] for k in irange])/len(irange) #Find the average of n_ds values
            irange += n_ds #Increment the range

        #Handle the final section, which may not have size n_ds
        jjt = max(irange) + 1 #Temporary variable
        if jjt < n_hr: #If TRUE, then there is more data
            jrange = np.arange(jjt, n_hr) #Range of remaining data
            ds_ts[m_ds] = sum(orig_ts[k] for k in jrange)/len(jrange) #Average of remaining values
        
        ds_array.append(ds_ts) #Add down-sampled data to ouput list
    
    return ds_array