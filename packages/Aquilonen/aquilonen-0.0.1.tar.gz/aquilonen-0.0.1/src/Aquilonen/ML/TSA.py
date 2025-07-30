
from inspect import signature
from statsmodels.tsa.arima.model import ARIMA
from numpy.linalg import LinAlgError
import warnings
warnings.filterwarnings("ignore")
class ARIMA_with_cv(ARIMA):

    #Perform cross validation on ARIMA model
    #Intended to copy model hyperparameters including pdq and exog; endog is dynamic inside method
    #Folds are automatically created based on sample size e.g. roughly speaking, 100 samples ~ 100 folds
    #This method skips runs which trigger errors due to training sample size

    #only current argument is a scoring function

    #returns a dictionary that includes:
        #final_score (average score across all folds)
        #num_folds (number of folds)
        #score_list (a list of the score at each fold; if skipped, score = None)
        #success_flags (a list indicating if a sample size was applied or skipped)
        #error_type (a list containing the error type that occured if skipped; 
            #if not skipped, the type is None;
            #Currently only indicates Linear algorthim error or index error;
            #other error types just fall under 'Other')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def cross_validate(self, scoring_function):

        time_series_data = self.endog
        exog_tsd = self.exog
    
        score_sum = 0

        num_folds = 0
    
        num_total_samples= len(time_series_data)
    
        # display(self.order)
    
        loop_range = range(num_total_samples)
        
        success_flags = []

        score_list = []

        error_type = []
    
        for train_length in loop_range:

            try:
            
                train_set = time_series_data[:train_length]
                test_set = time_series_data[train_length:]
                try: 
                    exog_train_set = exog_tsd[:train_length]
                    exog_test_set = exog_tsd[train_length:]
                except TypeError as e:
                    # display(e)
                    exog_train_set = None
                    exog_test_set = None
                test_length = len(test_set)


                args_in = {}

                arima_sig_object = signature(ARIMA)
            
                parameter_iterable = arima_sig_object.parameters

                for param in parameter_iterable:

                    the_model_actually_has_that_attribute = hasattr(self, param)

                    # the_param_is_not_trend = not(param in ['trend', 'trend_offset'])

                    if the_model_actually_has_that_attribute:# and the_param_is_not_trend:
                        args_in[param] = getattr(self, param)

                args_in['endog'] = train_set
                # display(len(args_in['endog']))
                args_in['trend'] = 'n'
                args_in['exog'] = exog_train_set

                # display(args_in)

                model = ARIMA( **args_in
                )

        
                model = model.fit()
                predictions = model.forecast(steps=test_length, exog = exog_test_set)
                score = scoring_function(test_set, predictions)
                score_list.append(score)
                score_sum += score
                num_folds += 1
                #was successful
                success_flags.append(True)

                # display(score_sum)

                error_type.append(None)

            except LinAlgError:
                # print("failed")
                #was not successful
                success_flags.append(False)
                error_type.append('LinAlgError')
                score_list.append(None)
                continue

            except IndexError:
                success_flags.append(False)
                error_type.append('IndexError')
                score_list.append(None)

                continue

            except:
                success_flags.append(False)
                error_type.append('Other')
                score_list.append(None)

                continue



    
        # num_folds = num_total_samples - min_samples_to_make_tsa_work
    
        final_score = score_sum/num_folds

        results = {}
        #this score is averaged across all folds
        results['final_score'] = final_score
        results['num_folds'] = num_folds
        results['scores'] = score_list
        results['success_flags'] = success_flags
        results['error_type'] = error_type
    
        return results
    

    
# from statsmodels.tsa.arima.model import ARIMA

# from sklearn.metrics import mean_squared_error

# fake_set = range(100)

# from pandas import Series

# fake_set = Series(fake_set)

# model = Custom_ARIMA(
#     fake_set
#     )

# results = model.cross_validate(scoring_function=mean_squared_error)
# #plot
# import matplotlib.pyplot as plt
# plt.plot(results['scores'])
# plt.show()
