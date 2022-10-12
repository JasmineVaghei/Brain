import mne
import numpy as np
from params_classification import Param
from sklearn.model_selection import train_test_split, ShuffleSplit
import rnn

def create_model_multi(raw, tmin, tmax):
    
    param = Param()
    events, _ = mne.events_from_annotations(raw)
    events = events[np.in1d(events[:, 2], (2, 3, 4, 5, 6)), :]

     
    epochs = mne.Epochs(raw, events, dict(left=2, right=3, down=4, up= 5, stop=6), tmin, tmax,
                        picks=("C3", "Cz", "C4"), baseline=None, preload=True)
    
    scalings = dict(eeg=param.scaling)
    scaler = mne.decoding.Scaler(epochs.info, scalings=scalings)
    X = epochs.get_data()
    X = scaler.fit_transform(X)

    Y = epochs.events[:, 2]             # event names were changed to start in ascending order, starting from 0
    Y = np.where(Y == 2, 0, Y)
    Y = np.where(Y == 3, 1, Y)
    Y = np.where(Y == 4, 2, Y)
    Y = np.where(Y == 5, 3, Y)
    Y = np.where(Y == 6, 4, Y)
   
    # print("Y.shape",Y.shape)

    X = np.expand_dims(X, 3)

    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=param.test_part,
                                                    random_state=0, shuffle=True)
    
    val = round(param.validation_part * x_train.shape[0])

    shuffle_split = ShuffleSplit(n_splits=param.cross_val_iter, test_size=val, random_state=0)
    val_results = []
    test_results = []
    iter_counter = 0

    # Monte-carlo cross-validation

    for train, validation in shuffle_split.split(x_train):
        iter_counter = iter_counter + 1
        print(iter_counter, "/", param.cross_val_iter, " cross-validation iteration")
        model = rnn.RNN(x_train.shape[1], x_train.shape[2], param)             # choose the network and feed input/output parameters
        # model = cnn.CNN(x_train.shape[1], x_train.shape[2], param)
        
        validation_metrics = model.fit(x_train[train], y_train[train], x_train[validation], y_train[validation])  #train the model
        val_results.append(validation_metrics)

        test_metrics = model.evaluate(x_test, y_test)
        test_results.append(test_metrics)

    avg_val_results = np.round(np.mean(val_results, axis=0) * 100, 2)
    avg_val_results_std = np.round(np.std(val_results, axis=0) * 100, 2)
    
    print("val_results", val_results)
    print("avg_val_results", avg_val_results)
    print("avg_val_results_std", avg_val_results_std)
