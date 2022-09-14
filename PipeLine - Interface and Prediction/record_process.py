import time
import keras
import mne
import numpy as np
import pandas as pd

from EEGTools.Recorders.Unicorn_Recorder.unicorn_recorder import \
    Unicorn_recorder as Recorder

# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def process_data(data):
    """
    data format = numpy array of shape (channels, samples)
    """
  
    info = mne.create_info(ch_names=["Fz", "C3", "Cz", "C4", "Pz", "P07", "Oz", "P08"],
                          ch_types=['eeg'] * 8,
                          sfreq=250)
    # construct mne Raw object                      
    data_raw = mne.io.RawArray(data, info, verbose=False)
    
    # compute psd of frequencies between 0-50
    data_psd, _ = mne.time_frequency.psd_welch(data_raw, fmin=0, fmax=50, tmin=None, tmax=None,
                n_fft=250, n_overlap=125, n_per_seg=250, picks=None,
                proj=False, n_jobs=1, reject_by_annotation=True, average=None, verbose=False)
    # (channels, frequencies, time segments)
    # (8, 51, 500)
    print("psd data", data_psd.shape)
    features = extract_features(data_psd)
    print(pd.DataFrame(features).head())
    return pd.DataFrame(features)

# expects a dataset corresponding to the merged data of all subjects of one scenario


def compute_features(scenario_psd):
    # get frequency bands
    delta = scenario_psd[:, 0:4, :]
    theta = scenario_psd[:, 4:8, :]
    alpha = scenario_psd[:, 8:13, :]
    beta = scenario_psd[:, 12:31, :]
    gamma = scenario_psd[:, 31:51, :]

    # ASSUMPTION #
    # we take the average of the different frequencies defined in the ranges of δ (<4 Hz), θ (4–7 Hz),
    # α (8–12 Hz), β (12–30 Hz), and γ (31–50 Hz) to get a single representative value

    delta_mean = np.mean(delta, axis=1)
    theta_mean = np.mean(theta, axis=1)
    alpha_mean = np.mean(alpha, axis=1)
    beta_mean = np.mean(beta, axis=1)
    gamma_mean = np.mean(gamma, axis=1)

    # replace extreme value with the 5th and 95th percentile respectively
    absolute_features = [delta_mean, theta_mean,
                         alpha_mean, beta_mean, gamma_mean]
    for feature in absolute_features:
        p1s, p99s = np.percentile(feature, [1, 99], axis=1)
        for channel, (p1, p99) in enumerate(zip(p1s, p99s)):
            feature[channel, feature[channel] < p1] = p1
            feature[channel, feature[channel] > p99] = p99

    # calculate some ratios given in the paper:
    # Barua, Shaibal, Mobyen Uddin Ahmed, and Shahina Begum. "Towards intelligent data analytics:
    # A case study in driver cognitive load classification." Brain sciences 10.8 (2020): 526.
    r1 = (alpha_mean + theta_mean)/beta_mean
    r2 = alpha_mean/beta_mean
    r3 = (alpha_mean + theta_mean)/(alpha_mean + beta_mean)
    r4 = theta_mean/beta_mean

    # construct dictionary with all features for each column for easy transformation to pandas dataframe later
    columns = {
        "Fz_delta": delta_mean[0, :],
        "Fz_theta": theta_mean[0, :],
        "Fz_alpha": alpha_mean[0, :],
        "Fz_beta": beta_mean[0, :],
        "Fz_gamma": gamma_mean[0, :],
        "Fz_r1": r1[0, :],
        "Fz_r2": r2[0, :],
        "Fz_r3": r3[0, :],
        "Fz_r4": r4[0, :],

        "C3_delta": delta_mean[1, :],
        "C3_theta": theta_mean[1, :],
        "C3_alpha": alpha_mean[1, :],
        "C3_beta": beta_mean[1, :],
        "C3_gamma": gamma_mean[1, :],
        "C3_r1": r1[1, :],
        "C3_r2": r2[1, :],
        "C3_r3": r3[1, :],
        "C3_r4": r4[1, :],

        "Cz_delta": delta_mean[2, :],
        "Cz_theta": theta_mean[2, :],
        "Cz_alpha": alpha_mean[2, :],
        "Cz_beta": beta_mean[2, :],
        "Cz_gamma": gamma_mean[2, :],
        "Cz_r1": r1[2, :],
        "Cz_r2": r2[2, :],
        "Cz_r3": r3[2, :],
        "Cz_r4": r4[2, :],

        "C4_delta": delta_mean[3, :],
        "C4_theta": theta_mean[3, :],
        "C4_alpha": alpha_mean[3, :],
        "C4_beta": beta_mean[3, :],
        "C4_gamma": gamma_mean[3, :],
        "C4_r1": r1[3, :],
        "C4_r2": r2[3, :],
        "C4_r3": r3[3, :],
        "C4_r4": r4[3, :],

        "Pz_delta": delta_mean[4, :],
        "Pz_theta": theta_mean[4, :],
        "Pz_alpha": alpha_mean[4, :],
        "Pz_beta": beta_mean[4, :],
        "Pz_gamma": gamma_mean[4, :],
        "Pz_r1": r1[4, :],
        "Pz_r2": r2[4, :],
        "Pz_r3": r3[4, :],
        "Pz_r4": r4[4, :],

        "P07_delta": delta_mean[5, :],
        "P07_theta": theta_mean[5, :],
        "P07_alpha": alpha_mean[5, :],
        "P07_beta": beta_mean[5, :],
        "P07_gamma": gamma_mean[5, :],
        "P07_r1": r1[5, :],
        "P07_r2": r2[5, :],
        "P07_r3": r3[5, :],
        "P07_r4": r4[5, :],

        "Oz_delta": delta_mean[6, :],
        "Oz_theta": theta_mean[6, :],
        "Oz_alpha": alpha_mean[6, :],
        "Oz_beta": beta_mean[6, :],
        "Oz_gamma": gamma_mean[6, :],
        "Oz_r1": r1[6, :],
        "Oz_r2": r2[6, :],
        "Oz_r3": r3[6, :],
        "Oz_r4": r4[6, :],

        "P08_delta": delta_mean[7, :],
        "P08_theta": theta_mean[7, :],
        "P08_alpha": alpha_mean[7, :],
        "P08_beta": beta_mean[7, :],
        "P08_gamma": gamma_mean[7, :],
        "P08_r1": r1[7, :],
        "P08_r2": r2[7, :],
        "P08_r3": r3[7, :],
        "P08_r4": r4[7, :]
    }

    return columns

# wrapper function that removes any nan values from the extracted features (can happen because of division by 0)


def extract_features(psd_data):
    data = compute_features(psd_data)
    for key, value in data.items():
        if np.isnan(value).any():
            value_new = np.nan_to_num(value, copy=True, nan=0.0)
            data.update({key: value_new})
    return data


def load_models():
    model = keras.models.load_model("my_model")
    return model


categories = ["Driver Driving/Low MWL", "Driver Distracted/ High MWL"]

if __name__ == "__main__":
    rec = Recorder()  # Instantiate the recorder
    rec.connect()  # Connect to the EEG device
    var = True
    rec.start_recording()  # start recording and collect the data in buffer
    model = load_models()
    f = open("predict.txt", 'w')
    while var:
        time.sleep(1)  # Records for 1s. 1s = 1 datapoint 
        rec.refresh()  # empty the buffer so that the recorder has access to the data
        data = rec.get_data()  # Returns data from beginning of the recording to the last refresh
        print("shape of recorded data", data.shape)
        current_data = data[0:8,-rec.get_sfreq():]
        print("shape of recorded current_data", current_data.shape)
        proc_data = process_data(current_data)
        proc_data.to_csv(path_or_buf=str(data.shape[1])+".csv")
        #proc_data.to_csv('mydata.csv', index=False)
        print(proc_data.shape)
        print(proc_data)
        predict = model.predict([proc_data])
        print(predict)
        f.write(str(int(predict[0][0])) + "\n")
        f.flush()  
        for prediction in predict:
            if prediction[0]==1.:
                print("Driver distracted")
            else:
                print('driver driving')
    rec.stop_recording()
    rec.disconnect()
