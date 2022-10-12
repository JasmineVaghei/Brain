class Param:
    
    def __init__(self):
        
        self.test_part = 0.3  # part of the data for the test set
        self.validation_part = 0.3  # part of the data for the validation set
        self.cross_val_iter = 10  # number of the iterations of the Monte*carlo cross-validation
        self.epochs = 3 # number of the iterations of the neural network training
        self.verbose = 2  # verbose parameter