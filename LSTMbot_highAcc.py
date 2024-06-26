import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import tensorflow as tf
from keras.models import Model
from keras.layers import Dense, Dropout, LSTM, Input, Activation
from keras import optimizers
from sklearn.metrics import mean_squared_error

if __name__ == "__main__":
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2020, 1, 1)
    ticker_symbol = "TLSA"
    train_split = 0.7
    # Define the number of data points to use as input features for the model
    data_set_points = 21

stock_df = yf.download(tickers=ticker_symbol, start=start_date, end=end_date)
new_df = stock_df[['Adj Close']].copy()

# Define a function to prepare the train and test data for the model
def prepare_train_test_split(new_df, data_set_points, train_split):
    # Reset the index of the dataframe and drop the first row
    new_df.reset_index(inplace=True)
    new_df.drop(0, inplace=True)
    split_index = int(len(new_df) * train_split)
    train_data = new_df[:split_index]
    test_data = new_df[split_index:].reset_index(drop=True)
    # Calculate the difference between consecutive values of the adjusted close price for both train and test sets
    train_diff = train_data['Adj Close'].diff().dropna().values
    test_diff = test_data['Adj Close'].diff().dropna().values
    # Create the input features for the model by taking data_set_points number of values from the train_diff array
    X_train = np.array([train_diff[i : i + data_set_points] for i in range(len(train_diff) - data_set_points)])
    # Create the output labels for the model by taking the next value after data_set_points number of values from the train_diff array
    y_train = np.array([train_diff[i + data_set_points] for i in range(len(train_diff) - data_set_points)])
    # Create a validation set from the last 10% of the train_data
    y_valid = train_data['Adj Close'].tail(len(y_train) // 10).values
    # Reshape the validation set to match the output shape of the model
    y_valid = y_valid.reshape(-1, 1)
    # Create the input features for the test set by taking data_set_points number of values from the test_diff array
    X_test = np.array([test_diff[i : i + data_set_points] for i in range(len(test_diff) - data_set_points)])
    # Create the output labels for the test set by taking the next value after data_set_points number of values from the test_data dataframe
    y_test = test_data['Adj Close'].shift(-data_set_points).dropna().values
    # Return the train and test sets as numpy arrays
    return X_train, y_train, X_test, y_test, test_data

def create_lstm_model(X_train, y_train, data_set_points):
    tf.random.set_seed(20)
    np.random.seed(10)
    lstm_input = Input(shape=(data_set_points, 1), name='lstm_input')
    inputs = LSTM(21, name='lstm_0', return_sequences=True)(lstm_input)
    inputs = Dropout(0.1, name='dropout_0')(inputs)
    inputs = LSTM(32, name='lstm_1')(inputs)
    inputs = Dropout(0.05, name='dropout_1')(inputs)
    inputs = Dense(32, name='dense_0')(inputs)
    inputs = Dense(1, name='dense_1')(inputs)
    output = Activation('linear', name='output')(inputs)
    model = Model(inputs=lstm_input, outputs=output)
    adam = optimizers.Adam(lr=0.002)
    model.compile(optimizer=adam, loss='mse')
    model.fit(x=X_train, y=y_train, batch_size=15, epochs=25, shuffle=True, validation_split=0.1)
    return model

# Prepare the train and test data sets
X_train, y_train, X_test, y_test, test_data = prepare_train_test_split(new_df, data_set_points, train_split)
model = create_lstm_model(X_train, y_train, data_set_points)
y_pred = model.predict(X_test)
y_pred = y_pred.flatten()
actual1 = np.array([test_data['Adj Close'][i + data_set_points] for i in range(len(test_data) - data_set_points)])
actual2 = actual1[:-1]
data = np.add(actual2, y_pred)
plt.gcf().set_size_inches(12, 8, forward=True)
plt.title('Plot of real price and predicted price against number of days for test set')
plt.xlabel('Number of days')
plt.ylabel('Adjusted Close Price($)')
plt.plot(actual1[1:], label='Actual Price')
plt.plot(data, label='Predicted Price')
print(mean_squared_error(actual1[1:], data, squared = False))
plt.legend(['Actual Price', 'Predicted Price'])
plt.show()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@%=-----:#**+++##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%##*+****:------*@@@
#@@@@@@@@@@*....:.--.:.-:.++=*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*+=+.:-.:.--.:....:%@@@@@
#@@@@@@@@@@@@@@=+-:...+=-:::::....-##=*@@@@@@@@@@@@@@@@@@@@@@@@@@@@*=%#-.....:-::--+....-++*@@@@@@@@@
#@@@@@@@@@@@@@#+##%##*@%#===-..:::::.-.-:*@@@@@@@@@@@@@@@@@@@@@@*--.-.::::...-==+#%%###%###*%@@@@@@@@
#@@@@@@@@@@@@@%:..:..::.-=+*##@@@+=-.-::.::%@@@@@@@@@@@@@@@@@@%:-.::::-=+@@@##**--.::..:.:.+@@@@@@@@@
#@@@@@@@@@@@@@@@*--:.----:.:::.:=++-:...=.-@@@@@%=:::--%@@@@@@%-.=...:-++=:...:.:-:::.:--=@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@%@#+*=-=**+=+--..-+@@@@*:=-:#=..:%@@@@@@@=-..:=+++#*--=*+#@%@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@%=----=-==++::=++-==:.-.+@@@@@@%%-.....=@@@@@@@+.-.:-===+=.-+++-:=----=#@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@%+=:.::.:..:.-:-%+...::=@@@@@@@@*-.:..+@@@@@@@=::..:+%-::...-..::.:=+%@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@#%@%%%%@%%###%:.-:::*@@@@#=:-:...=@@@@@*:::-..%###%@@%%%@@%#@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@*--:::-:...:#@@-=-=.-=:*@*:-:.==.:=:+@#:=-.=-=-@@#:..:::.::=-*@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@=:::::.-@@@*++*##*:-::-::=.::::.:.=.---.:-+##*++*@@%-.:::::-@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@###=**-:::++*###%=-==.+---=-=:-*.==-=%###*+=:::-**+##*@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@-.:..::.=%##--.-=*#**===:.--.:-+-**#*--:--##%-.::..:.-@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@%%@#-=%@*+..:-%-=-*@#:+:..--..:#:*@*-=-#-:..+#@#=-%@%#@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-::=+%%#-=++-*@%=.=--=:=%%+-*+--#%%+=::-@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@=#%%@+:-.-*::*@@@-+--+-@@@*:-*-.-:=@%%#-@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@==:-+%+-*%*+*#+**=%*+*%*=+%+-:==@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%@@@@+-::**+:.=*+:::+@@@@%%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*-::-%@*==*@%--:-*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@..-.*@#--:.*@#:::-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%@@@@@@@:-++@@:-+==-@@*+-:@@@@@@@%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*=@#=@@+--@@@@+-=----+@@@@-=+@@+*@%=%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*##-+-==*@@@@@+=%=*#-%++@@@@@#==:===%+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#+=:+=@@%@%%+.-=+#--*+=-.=@%@%@@=+--=*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*#%+%*@@@@*::-=#-:==:=#--::+@@@@*#*+#+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%-@+-@@@@@#*-=-:=+-::-=:*#%@@@@-+@-#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#:+#=:=+#-:-%=-#%@@@@@@%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#=++#=:=+=--=%=+=*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@##@+#*====-=*%+@%*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%*+%@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@